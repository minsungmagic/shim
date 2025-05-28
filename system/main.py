import simpy
import random
from Farm import Factory
from order import order_generator


# 시뮬레이션 실행
def run_simulation():
    random.seed(42)
    env = simpy.Environment()
    factory = Factory(env, num_printers=10)
    env.process(order_generator(env, factory, order_interval=40))
    env.run(until=500)
    factory.metrics.save_to_csv()  # 시뮬레이션 종료 후 CSV 저장

if __name__ == "__main__":
    run_simulation()
