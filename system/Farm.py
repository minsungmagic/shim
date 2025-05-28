import simpy
import random
from collections import deque
from printer import Printer
from inventory import Inventory
from Metrics import Metrics

# 공장 클래스
class Factory:
    def __init__(self, env, num_printers=10):
        self.env = env
        self.filament = simpy.Container(env, init=100, capacity=100)
        self.filament.name = "필라멘트"
        self.paint = simpy.Container(env, init=50, capacity=50)
        self.paint.name = "페인트"
        self.metrics = Metrics(env, num_printers)
        self.printers = [Printer(env, i, self.metrics) for i in range(num_printers)]  # 프린터 리스트 생성
        self.filament_inventory = Inventory(env, self, self.filament, s=20, S=100, restock_time=10)
        self.paint_inventory = Inventory(env, self, self.paint, s=10, S=50, restock_time=7)
        self.order_queue = deque()  # FIFO 주문 큐
        self.total_products = 0  # 전체 생성된 제품 수
        self.completed_products = 0  # 완료된 제품 수
        self.packaging_store = simpy.Store(env)  # 패키징 대기 제품
        self.env.process(self.process_orders())  # 주문 처리 프로세스 시작

    def add_order(self, order_id, num_products):
        self.order_queue.append((order_id, num_products))  # 큐에 주문 추가
        self.total_products += num_products

    def can_accept_order(self):
        # 패키징 대기 제품이 전체 제품의 70% 미만인지 확인
        if self.total_products == 0:
            return True
        return (len(self.packaging_store.items) / self.total_products) < 0.7

    def process_orders(self):
        while True:
            if self.order_queue:
                order_id, num_products = self.order_queue.popleft()  # FIFO로 주문 꺼내기
                yield self.env.process(self.process_order(order_id, num_products))
            yield self.env.timeout(1)

    def process_order(self, order_id, num_products):
        product_processes = []
        completed_products = []
        for product_id in range(num_products):
            # 사용 가능한 프린터 선택
            available_printers = [p for p in self.printers if len(p.resource.users) == 0 or p.resource.count < p.resource.capacity]
            if not available_printers:
                print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} - 모든 프린터 사용 중, 대기")
            printer = random.choice(available_printers) if available_printers else self.printers[0]
            process = self.env.process(printer.process_product(order_id, product_id, self.filament, self.paint))
            product_processes.append(process)
            completed_products.append((order_id, product_id))
        yield self.env.all_of(product_processes)  # 모든 제품 처리가 완료될 때까지 대기
        # 패키징 대기열에 제품 추가
        for product in completed_products:
            self.packaging_store.put(product)
        self.completed_products += num_products
        self.metrics.record_order(order_id, num_products)  # 주문 완료 기록
        print(f"{self.env.now:.2f}분: 주문 {order_id} 모든 제품 생산 완료, 패키징 대기열에 추가 (총 {num_products}개 제품)")
        # 패키징 프로세스 시작
        yield self.env.process(self.package_order(order_id, num_products))

    def package_order(self, order_id, num_products):
        products = []
        for _ in range(num_products):
            product = yield self.packaging_store.get()
            products.append(product)
        yield self.env.timeout(5)  # 패키징 5분 소요
        print(f"{self.env.now:.2f}분: 주문 {order_id} 패키징 완료 (총 {num_products}개 제품)")