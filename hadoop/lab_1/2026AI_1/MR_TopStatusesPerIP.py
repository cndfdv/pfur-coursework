from mrjob.job import MRJob
from mrjob.step import MRStep

class TopStatusesPerIP(MRJob):

    def steps(self):
        # Убираем step2_mapper. mrjob связывает reducer1 -> reducer2 напрямую
        return [
            MRStep(mapper=self.step1_mapper, reducer=self.step1_reducer),
            MRStep(reducer=self.step2_reducer)
        ]

    # ==========================================
    # ШАГ 1: Подсчет частоты статусов для каждого IP
    # ==========================================
    
    def step1_mapper(self, key, line):
        parts = line.split('\t')
        if len(parts) == 2:
            ip, status = parts
            yield ip, status

    def step1_reducer(self, ip, statuses):
        counts = {}
        total_requests = 0
        
        for status in statuses:
            counts[status] = counts.get(status, 0) + 1
            total_requests += 1
            
        # Передаем обычный словарь. mrjob сам сериализует его под капотом.
        result_data = {
            'total': total_requests,
            'counts': counts
        }
        yield ip, result_data

    # ==========================================
    # ШАГ 2: Фильтрация и выбор Топ-3 (Данные идут напрямую из reducer1)
    # ==========================================
    
    def step2_reducer(self, ip, data_list):
        # Так как ключи IP уникальны после Шага 1, в data_list будет ровно 1 элемент
        data = next(data_list)
        
        total = data['total']
        counts = data['counts']
        
        # Фильтр: только если запросов > 4
        if total > 4:
            # Сортируем статусы по убыванию частоты (x[1] - это count)
            sorted_statuses = sorted(
                counts.items(), key=lambda x: x[1], reverse=True
            )
            
            # Берем топ-3
            top_3 = sorted_statuses[:3]
            
            # Форматируем красивый вывод
            top_3_str = ", ".join(
                [f"{status}({count})" for status, count in top_3]
            )
            yield ip, f"Total: {total} | Top 3 statuses: {top_3_str}"

if __name__ == '__main__':
    TopStatusesPerIP.run()
