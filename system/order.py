import random
import numpy as np

def order_generator(env, factory, order_interval):
    order_id = 0
    while True:
        if factory.can_accept_order():
            yield env.timeout(np.random.exponential(order_interval))
            num_products = random.randint(30, 50)
            print(f"{env.now:.2f}: 주문 {order_id} 수주 (제품 {num_products}개)")
            factory.add_order(order_id, num_products)
            order_id += 1
        else:
            print(f"{env.now:.2f}: 패키징 대기 제품이 70% 미만, 주문 수주 불가가")
            yield env.timeout(20) #실패시 대기 시간 증가
