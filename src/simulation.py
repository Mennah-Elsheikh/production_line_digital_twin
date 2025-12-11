import random
import simpy
import pandas as pd
import numpy as np
from collections import defaultdict
from .config import SEED, SIM_TIME, INTERARRIVAL_MEAN, MACHINES, PROC_DISTRIBUTION, WARMUP_TIME

random.seed(SEED)
np.random.seed(SEED)

class Product:
    def __init__(self, id, created_time):
        self.id = id
        self.created_time = created_time
        self.timestamps = {} # record enter/leave times per station

class MachineStation:
    def __init__(self, env, name, capacity, proc_mean, mtbf=None, mttr=None):
        self.env = env
        self.name = name
        # Use PriorityResource to allow breakdowns (priority 0) to preempt production (priority 1)
        self.resource = simpy.PriorityResource(env, capacity=capacity)
        self.proc_mean = proc_mean
        self.mtbf = mtbf
        self.mttr = mttr
        
        self.busy_time = 0.0
        self.downtime = 0.0  # Track total downtime
        self.processed = 0
        
        # Start breakdown process if parameters are provided
        if self.mtbf and self.mttr:
            self.env.process(self.breakdown_process())

    def breakdown_process(self):
        """Simulate machine failures and repairs"""
        while True:
            # Time until next failure
            # We use exponential distribution for failures (memoryless property)
            time_to_failure = random.expovariate(1.0 / self.mtbf)
            yield self.env.timeout(time_to_failure)
            
            # Machine fails - request resource with higher priority (0)
            # This waits for current processing to finish (non-preemptive failure)
            # which is realistic for short cycle times
            with self.resource.request(priority=0) as req:
                yield req
                
                # Machine is down
                repair_time = random.expovariate(1.0 / self.mttr)
                yield self.env.timeout(repair_time)
                self.downtime += repair_time

    def sample_process_time(self):
        if PROC_DISTRIBUTION == 'exp':
            return random.expovariate(1.0 / self.proc_mean)
        else:
            return self.proc_mean
        
    def record_processing(self, duration):
        """Record processing stats"""
        self.busy_time += duration
        self.processed += 1
        
    def reset_stats(self):
        """Reset statistics (for warm-up)"""
        self.busy_time = 0.0
        self.downtime = 0.0
        self.processed = 0

class ProductionLineModel:
    def __init__(self, env, machines_config, interarrival_mean, warmup_time=0):
        self.env = env
        self.interarrival_mean = interarrival_mean
        self.warmup_time = warmup_time
        # Pass MTBF and MTTR to MachineStation
        self.machines = [
            MachineStation(
                env, 
                m['name'], 
                m['capacity'], 
                m['proc_mean'],
                m.get('MTBF', None),
                m.get('MTTR', None)
            ) for m in machines_config
        ]
        self.store = [simpy.Store(env) for _ in self.machines] # queues before each station
        self.finished = simpy.Store(env)
        self.products = {}
        self.stats = []
        self.product_count = 0
        
        # Queue and WIP tracking
        self.queue_snapshots = []  # Track queue lengths over time
        self.wip_snapshots = []    # Track work-in-progress over time
        self.monitor_interval = 5  # Monitor every 5 minutes

        # start station processes
        for i, machine in enumerate(self.machines):
            # Create a process for EACH unit of capacity
            for _ in range(machine.resource.capacity):
                self.env.process(self.station_process(i))

        # arrival process
        self.env.process(self.arrival_process())
        
        # monitoring process
        self.env.process(self.monitor_process())
        
        # warmup process
        self.env.process(self.warmup_process())

        

    def arrival_process(self):
        while True:
            yield self.env.timeout(random.expovariate(1.0 / self.interarrival_mean))
            pid = f'P{self.product_count}'
            p = Product(pid, self.env.now)
            self.products[pid] = p
            self.product_count += 1
            
            # Record queue enter time for first machine
            p.timestamps[f'{self.machines[0].name}_queue_enter'] = self.env.now
            
            # put into first queue
            yield self.store[0].put(p)

    def monitor_process(self):
        """Monitor queue lengths and WIP at regular intervals"""
        while True:
            yield self.env.timeout(self.monitor_interval)
            
            # Skip data collection during warm-up
            if self.env.now < self.warmup_time:
                continue

            # Record queue lengths
            queue_snapshot = {'time': self.env.now}
            for i, (machine, store) in enumerate(zip(self.machines, self.store)):
                queue_snapshot[f'{machine.name}_queue'] = len(store.items)
            self.queue_snapshots.append(queue_snapshot)
            
            # Record WIP (products in system but not finished)
            wip = self.product_count - len(self.finished.items)
            self.wip_snapshots.append({'time': self.env.now, 'wip': wip})
            
    def warmup_process(self):
        """Wait for warm-up time then reset statistics"""
        if self.warmup_time > 0:
            yield self.env.timeout(self.warmup_time)
            print(f"Warm-up complete at {self.env.now:.1f} min. Resetting stats...")
            
            # Reset machine stats
            for m in self.machines:
                m.reset_stats()
                
            # Clear accumulated products that finished during warm-up (optional but cleaner stats)
            # self.stats = [] # We don't use this list much, but good to know
            
            # Note: We don't delete products from self.products as we need them for flow validation
            # But collect_results will filter by timestamp anyway


    def station_process(self, idx):
        machine = self.machines[idx]
        in_store = self.store[idx]
        out_store = self.store[idx + 1] if idx + 1 < len(self.store) else self.finished
        
        while True:
            # Wait for product from queue (Store)
            product = yield in_store.get()
            
            # Service start
            service_start = self.env.now
            product.timestamps[f'{machine.name}_service_start'] = service_start
            
            # Calculate wait time (Time since entered queue)
            queue_enter = product.timestamps.get(f'{machine.name}_queue_enter', service_start)
            wait_time = service_start - queue_enter
            product.timestamps[f'{machine.name}_wait_time'] = wait_time
            
            # Request machine resource with priority 1 (Lower than breakdown priority 0)
            with machine.resource.request(priority=1) as req:
                yield req
                
                # We start service only after we get the resource
                # Note: service_service timestamp recorded at start of wait for resource above 
                # might actally include waiting for breakdown if we put it before request.
                # However, usually service start is when resource is acquired.
                # Let's adjust service_start to be AFTER resource acquisition for accuracy.
                
                service_start = self.env.now
                product.timestamps[f'{machine.name}_service_start'] = service_start
                # Re-calc wait time to include waiting for broken machine
                wait_time = service_start - queue_enter
                product.timestamps[f'{machine.name}_wait_time'] = wait_time

                # Process
                proc_time = machine.sample_process_time()
                yield self.env.timeout(proc_time)
                
                # Record stats
                machine.record_processing(proc_time)
                product.timestamps[f'{machine.name}_service_end'] = self.env.now

            # Prepare for next station
            if idx + 1 < len(self.machines):
                next_machine_name = self.machines[idx+1].name
                product.timestamps[f'{next_machine_name}_queue_enter'] = self.env.now

            # put to next queue
            yield out_store.put(product)

    def collect_results(self):
        # gather finished products
        finished = []
        while not self.finished.items == []:
            finished.extend(self.finished.items)
            break
        # instead, collect all products that have end timestamp for last machine
        results = []
        last_machine_name = self.machines[-1].name
        for pid, p in self.products.items():
            key_end = f'{last_machine_name}_service_end'
            if key_end in p.timestamps:
                # Filter out products that finished during warm-up
                if p.timestamps[key_end] < self.warmup_time:
                    continue
                    
                entry = {
                    'id': pid,
                    'created': p.created_time,
                    'finished': p.timestamps[key_end],
                    'lead_time': p.timestamps[key_end] - p.created_time,
                }
                # Add per-machine times
                for m in self.machines:
                    s = f'{m.name}_service_start'
                    e = f'{m.name}_service_end'
                    w = f'{m.name}_wait_time'
                    entry[f'{m.name}_start'] = p.timestamps.get(s, None)
                    entry[f'{m.name}_end'] = p.timestamps.get(e, None)
                    entry[f'{m.name}_wait_time'] = p.timestamps.get(w, 0.0)
                results.append(entry)
        df = pd.DataFrame(results)
        return df
    
    def machine_stats(self):
        rows = []
        for m in self.machines:
            # Utilization = Total Busy Time / (Simulation Time * Capacity)
            # This accounts for parallel processing capacity
            # Adjust simulation time for warm-up
            effective_sim_time = self.env.now - self.warmup_time
            if effective_sim_time > 0:
                util = m.busy_time / (float(effective_sim_time) * m.resource.capacity)
                avail = 1.0 - (m.downtime / (float(effective_sim_time) * m.resource.capacity))
            else:
                util = 0.0
                avail = 1.0
            
            rows.append({
                'machine': m.name,
                'capacity': m.resource.capacity,
                'processed': m.processed,
                'busy_time': m.busy_time,
                'downtime': m.downtime,
                'utilization': util,
                'availability': avail
            })
        return pd.DataFrame(rows)
    
    def get_queue_data(self):
        """Return queue length snapshots as DataFrame"""
        return pd.DataFrame(self.queue_snapshots)
    
    def get_wip_data(self):
        """Return WIP snapshots as DataFrame"""
        return pd.DataFrame(self.wip_snapshots)


def run_simulation(sim_time=SIM_TIME, warmup_time=WARMUP_TIME, verbose=False):
    env = simpy.Environment()
    model = ProductionLineModel(env, MACHINES, INTERARRIVAL_MEAN, warmup_time=warmup_time)
    env.run(until=sim_time)
    df_results = model.collect_results()
    df_mstats = model.machine_stats()
    df_queue = model.get_queue_data()
    df_wip = model.get_wip_data()
    if verbose:
        print(df_mstats)
        print(df_results.head())
    return df_results, df_mstats, df_queue, df_wip
