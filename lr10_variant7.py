import heapq
import random
import time
from collections import deque

INF = float("inf")


def dijkstra_array(graph, start):
    n = len(graph)
    dist = [INF] * n
    parent = [-1] * n
    used = [False] * n
    dist[start] = 0

    for _ in range(n):
        v = -1
        best = INF
        for i in range(n):
            if not used[i] and dist[i] < best:
                v, best = i, dist[i]
        if v == -1:
            break
        used[v] = True
        for u, w in graph[v]:
            if dist[v] + w < dist[u]:
                dist[u] = dist[v] + w
                parent[u] = v
    return dist, parent


def dijkstra_heap(graph, start):
    n = len(graph)
    dist = [INF] * n
    parent = [-1] * n
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, v = heapq.heappop(heap)
        if d != dist[v]:
            continue
        for u, w in graph[v]:
            nd = d + w
            if nd < dist[u]:
                dist[u] = nd
                parent[u] = v
                heapq.heappush(heap, (nd, u))
    return dist, parent


def restore_path(parent, target):
    path = []
    while target != -1:
        path.append(target)
        target = parent[target]
    return path[::-1]


def make_grid(k, seed=42):
    rng = random.Random(seed)
    graph = [[] for _ in range(k * k)]

    def add_edge(a, b):
        w = rng.randint(1, 100)
        graph[a].append((b, w))
        graph[b].append((a, w))

    for r in range(k):
        for c in range(k):
            v = r * k + c
            if c + 1 < k:
                add_edge(v, v + 1)
            if r + 1 < k:
                add_edge(v, v + k)
    return graph


def topological_order(tasks):
    indeg = {v: len(data[1]) for v, data in tasks.items()}
    succ = {v: [] for v in tasks}
    for v, (_, preds) in tasks.items():
        for p in preds:
            if p not in tasks:
                raise ValueError("Неизвестная предшествующая работа: " + p)
            succ[p].append(v)

    q = deque(v for v in tasks if indeg[v] == 0)
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for u in succ[v]:
            indeg[u] -= 1
            if indeg[u] == 0:
                q.append(u)

    if len(order) != len(tasks):
        raise ValueError("В сетевом графике есть цикл")
    return order, succ


def critical_path(tasks):
    order, succ = topological_order(tasks)
    es, ef = {}, {}
    for v in order:
        duration, preds = tasks[v]
        es[v] = max((ef[p] for p in preds), default=0)
        ef[v] = es[v] + duration

    total = max(ef.values())
    ls, lf = {}, {}
    for v in reversed(order):
        duration = tasks[v][0]
        lf[v] = min((ls[u] for u in succ[v]), default=total)
        ls[v] = lf[v] - duration

    reserve = {v: ls[v] - es[v] for v in tasks}
    critical = [v for v in order if reserve[v] == 0]
    return total, es, ef, ls, lf, reserve, critical


def draw_gantt(tasks, es, ef, critical):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Для диаграммы Ганта установите matplotlib: pip install matplotlib")
        return

    names = list(tasks)
    fig, ax = plt.subplots(figsize=(10, 5))
    for y, name in enumerate(names):
        start = es[name]
        duration = tasks[name][0]
        color = "tomato" if name in critical else "steelblue"
        ax.barh(y, duration, left=start, color=color, edgecolor="black")
        ax.text(start + duration / 2, y, name, ha="center", va="center")
    ax.set_yticks(range(len(names)), names)
    ax.set_xlabel("Дни")
    ax.set_title("Диаграмма Ганта (критические работы выделены)")
    ax.grid(axis="x", alpha=0.3)
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig("gantt_variant7.png", dpi=150)
    plt.close(fig)
    print("Диаграмма сохранена: gantt_variant7.png")


if __name__ == "__main__":
    print("СРАВНЕНИЕ ДЕЙКСТРЫ ДЛЯ РЕШЁТОК")
    print(f"{'k':>5}{'n':>8}{'m':>10}{'массив, с':>14}{'куча, с':>12}")
    for k in (30, 50, 70):
        graph = make_grid(k, seed=42)
        n = k * k
        m = sum(map(len, graph)) // 2

        t0 = time.perf_counter()
        d1, _ = dijkstra_array(graph, 0)
        t_array = time.perf_counter() - t0

        t0 = time.perf_counter()
        d2, parent = dijkstra_heap(graph, 0)
        t_heap = time.perf_counter() - t0

        assert d1 == d2
        print(f"{k:>5}{n:>8}{m:>10}{t_array:>14.4f}{t_heap:>12.4f}")

    # Небольшой тестовый граф 3x3
    test = [
        [(1, 2), (3, 4)],
        [(0, 2), (2, 3), (4, 2)],
        [(1, 3), (5, 1)],
        [(0, 4), (4, 1), (6, 2)],
        [(1, 2), (3, 1), (5, 5), (7, 3)],
        [(2, 1), (4, 5), (8, 2)],
        [(3, 2), (7, 2)],
        [(4, 3), (6, 2), (8, 1)],
        [(5, 2), (7, 1)]
    ]
    dist, parent = dijkstra_heap(test, 0)
    print("\nТест 3x3: расстояние от 0 до 8 =", dist[8])
    print("Путь:", " -> ".join(map(str, restore_path(parent, 8))))

    tasks = {
        "A": (5, []), "B": (7, ["A"]), "C": (4, ["B"]),
        "D": (6, ["B"]), "E": (10, ["C"]), "F": (9, ["D"]),
        "G": (3, ["E", "F"]), "H": (4, ["C", "D"]),
        "I": (6, ["G"]), "J": (2, ["H", "I"])
    }
    total, es, ef, ls, lf, reserve, critical = critical_path(tasks)
    print("\nРАСЧЁТ КРИТИЧЕСКОГО ПУТИ")
    print(f"{'Работа':>8}{'t':>5}{'ES':>5}{'EF':>5}{'LS':>5}{'LF':>5}{'R':>5}")
    for v in tasks:
        print(f"{v:>8}{tasks[v][0]:>5}{es[v]:>5}{ef[v]:>5}{ls[v]:>5}{lf[v]:>5}{reserve[v]:>5}")
    print("Длительность проекта:", total, "дней")
    print("Критический путь:", " -> ".join(critical))
    draw_gantt(tasks, es, ef, critical)
