import random
import simpy
import pandas as pd
import numpy as np
from collections import defaultdict
from config import SEED, SIM_TIME, INTERARRIVAL_MEAN, MACHINES, PROC_DISTRIBUTION

random.seed(SEED)
np.random.seed(SEED)

class Product:
    def __init__(self, id, created_time):
        self.id = id
        self.created_time = created_time
        self.timestamps = {} # record enter/leave times per station

class MachineStation:
    def __init__(self, env, name, capacity, proc_mean):
        self.env = env
        self.name = name
        self.resource = simpy.Resource(env, capacity=capacity)
        self.proc_mean = proc_mean
        self.busy_time = 0.0
        self.last_start = None
        self.processed = 0

    def sample_process_time(self):
        if PROC_DISTRIBUTION == 'exp':
            return random.expovariate(1.0 / self.proc_mean)
        else:
            return self.proc_mean
        
    def start_service(self):
       # called when a unit begins service
       self.last_start = self.env.now

    def end_service(self):
       # called when a unit ends service
       if self.last_start is not None:
           self.busy_time += self.env.now - self.last_start
           self.last_start = None
       self.processed += 1

class ProductionLineModel:
    def __init__(self, env, machines_config, interarrival_mean):
        self.env = env
        self.interarrival_mean = interarrival_mean
        self.machines = [MachineStation(env, m['name'], m['capacity'], m['proc_mean']) for m in machines_config]
        self.store = [simpy.Store(env) for _ in self.machines] # queues before each station
        self.finished = simpy.Store(env)
        self.products = {}
        self.stats = []
        self.product_count = 0

        # start station processes
        for i, machine in enumerate(self.machines):
            self.env.process(self.station_process(i))

           # arrival process
        self.env.process(self.arrival_process())
        

    def arrival_process(self):
        while True:
            yield self.env.timeout(random.expovariate(1.0 / self.interarrival_mean))
            pid = f'P{self.product_count}'
            p = Product(pid, self.env.now)
            self.products[pid] = p
            self.product_count += 1
            # put into first queue
            yield self.store[0].put(p)

    def station_process(self, idx):
        machine = self.machines[idx]
        in_store = self.store[idx]
        out_store = self.store[idx + 1] if idx + 1 < len(self.store) else self.finished

        while True:
            product = yield in_store.get()
            arrive = self.env.now
            product.timestamps[f'{machine.name}_queue_enter'] = arrive


            with machine.resource.request() as req:
                yield req
                # start service
                service_start = self.env.now
                product.timestamps[f'{machine.name}_service_start'] = service_start
                machine.start_service()
                proc_time = machine.sample_process_time()
                yield self.env.timeout(proc_time)
                machine.end_service()
                product.timestamps[f'{machine.name}_service_end'] = self.env.now


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
                entry[f'{m.name}_start'] = p.timestamps.get(s, None)
                entry[f'{m.name}_end'] = p.timestamps.get(e, None)
            results.append(entry)
        df = pd.DataFrame(results)
        return df
    
    def machine_stats(self):
        rows = []
        for m in self.machines:
            rows.append({
            'machine': m.name,
            'capacity': m.resource.capacity,
            'processed': m.processed,
            'busy_time': m.busy_time,
            'utilization': m.busy_time / float(self.env.now) if self.env.now>0 else 0.0
            })
        return pd.DataFrame(rows)
    

def run_simulation(sim_time=SIM_TIME, verbose=False):
    env = simpy.Environment()
    model = ProductionLineModel(env, MACHINES, INTERARRIVAL_MEAN)
    env.run(until=sim_time)
    df_results = model.collect_results()
    df_mstats = model.machine_stats()
    if verbose:
        print(df_mstats)
        print(df_results.head())
    return df_results, df_mstats