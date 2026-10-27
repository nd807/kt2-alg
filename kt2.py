from collections import deque
from pathlib import Path


class DependencyGraph:
    def __init__(self):
        self.graph = {}

    def add_component(self, name):
        if name not in self.graph:
            self.graph[name] = []

    def add_dependency(self, source, target):
        self.add_component(source)
        self.add_component(target)
        if target not in self.graph[source]:
            self.graph[source].append(target)

    def load_file(self, filename):
        with open(filename, encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                name, dependencies = line.strip().split(":", 1)
                name = name.strip()
                self.add_component(name)
                for dependency in dependencies.split(","):
                    if dependency.strip():
                        self.add_dependency(name, dependency.strip())

    def get_topological_order(self):
        state = {}
        order = []

        def visit(component):
            if state.get(component, 0) == 1:
                return False
            if state.get(component, 0) == 2:
                return True
            state[component] = 1
            for dependency in self.graph[component]:
                if not visit(dependency):
                    return False
            state[component] = 2
            order.append(component)
            return True

        for component in self.graph:
            if not visit(component):
                return None
        return order

    def is_acyclic(self):
        return self.get_topological_order() is not None


class DependencyAnalyzer:
    def __init__(self, graph):
        self.graph = graph.graph

    def find_dependencies_bfs(self, start):
        if start not in self.graph:
            raise ValueError("Компонент не найден")
        visited = {start}
        queue = deque([start])
        levels = []
        while queue:
            level = []
            for _ in range(len(queue)):
                component = queue.popleft()
                for dependency in self.graph[component]:
                    if dependency not in visited:
                        visited.add(dependency)
                        queue.append(dependency)
                        level.append(dependency)
            if level:
                levels.append(level)
        return levels

    def find_dependencies_dfs(self, start):
        if start not in self.graph:
            raise ValueError("Компонент не найден")
        visited = {start}

        def visit(component):
            for dependency in self.graph[component]:
                if dependency not in visited:
                    visited.add(dependency)
                    visit(dependency)

        visit(start)
        visited.remove(start)
        return visited


def main():
    path = Path(__file__).with_name("dependencies.txt")
    if not path.exists():
        path.write_text("A: B, C\nB: D\nC: D, E\nD:\nE: B\n", encoding="utf-8")
    graph = DependencyGraph()
    graph.load_file(path)
    analyzer = DependencyAnalyzer(graph)
    order = graph.get_topological_order()
    print("Порядок сборки:", order if order is not None else "Обнаружен цикл")
    print("BFS для A:", analyzer.find_dependencies_bfs("A"))
    print("DFS для A:", sorted(analyzer.find_dependencies_dfs("A")))
    graph.add_dependency("D", "A")
    print("После добавления D -> A:", "Нет цикла" if graph.is_acyclic() else "Обнаружен цикл")


if __name__ == "__main__":
    main()
