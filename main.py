import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QVBoxLayout as DialogVBoxLayout,
    QCheckBox,
    QDateTimeEdit,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QDateTime

class Task:
    def __init__(self, name, priority, description, due_date=None):
        self.name = name
        self.priority = priority
        self.description = description
        self.due_date = due_date
        self.completed = False

    def __lt__(self, other):
        priorities = {'High': 0, 'Medium': 1, 'Low': 2}
        return priorities[self.priority] < priorities[other.priority]

class PriorityQueue:
    def __init__(self):
        self.heap = []

    def push(self, task):
        self.heap.append(task)
        self._heapify_up()

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        top = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down()
        return top

    def _heapify_up(self):
        current_index = len(self.heap) - 1
        while current_index > 0:
            parent_index = (current_index - 1) // 2
            if self.heap[current_index] < self.heap[parent_index]:
                self.heap[current_index], self.heap[parent_index] = (
                    self.heap[parent_index],
                    self.heap[current_index],
                )
                current_index = parent_index
            else:
                break

    def _heapify_down(self):
        current_index = 0
        while True:
            left_child_index = 2 * current_index + 1
            right_child_index = 2 * current_index + 2
            smallest = current_index

            if (
                left_child_index < len(self.heap)
                and self.heap[left_child_index] < self.heap[smallest]
            ):
                smallest = left_child_index

            if (
                right_child_index < len(self.heap)
                and self.heap[right_child_index] < self.heap[smallest]
            ):
                smallest = right_child_index

            if smallest != current_index:
                self.heap[current_index], self.heap[smallest] = (
                    self.heap[smallest],
                    self.heap[current_index],
                )
                current_index = smallest
            else:
                break

class TaskDetailsDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Details")
        self.setGeometry(200, 200, 400, 250)

        layout = DialogVBoxLayout()

        task_name_label = QLabel(f"Task Name: {task.name}")
        priority_label = QLabel(f"Priority: {task.priority}")
        description_label = QLabel(f"Description: {task.description}")
        due_date_label = QLabel(f"Due Date: {task.due_date}")
        completed_checkbox = QCheckBox(f"Completed: {'Yes' if task.completed else 'No'}")
        completed_checkbox.setEnabled(False)

        layout.addWidget(task_name_label)
        layout.addWidget(priority_label)
        layout.addWidget(description_label)
        layout.addWidget(due_date_label)
        layout.addWidget(completed_checkbox)

        self.setLayout(layout)

class TaskManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.priority_queue = PriorityQueue()

        # Create widgets
        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout(self.central_widget)

        self.task_name_label = QLabel('Task Name:', self)
        self.task_name_input = QLineEdit(self)

        self.priority_label = QLabel('Priority:', self)
        self.priority_combobox = QComboBox(self)
        self.priority_combobox.addItems(['High', 'Medium', 'Low'])

        self.task_description_label = QLabel('Description:', self)
        self.task_description_input = QTextEdit(self)

        self.due_date_label = QLabel('Due Date:', self)
        self.due_date_input = QDateTimeEdit(self)
        self.due_date_input.setDateTime(QDateTime.currentDateTime())

        self.add_task_button = QPushButton('Add Task', self)
        self.add_task_button.clicked.connect(self.add_task)

        self.remove_task_button = QPushButton('Remove Highest Priority Task', self)
        self.remove_task_button.clicked.connect(self.remove_task)

        self.task_table = QTableWidget(self)
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(['Task Name', 'Priority', 'Description', 'Due Date', 'Completed', 'Action'])
        self.layout.addWidget(self.task_table)

        self.layout.addWidget(self.task_name_label)
        self.layout.addWidget(self.task_name_input)
        self.layout.addWidget(self.priority_label)
        self.layout.addWidget(self.priority_combobox)
        self.layout.addWidget(self.task_description_label)
        self.layout.addWidget(self.task_description_input)
        self.layout.addWidget(self.due_date_label)
        self.layout.addWidget(self.due_date_input)
        self.layout.addWidget(self.add_task_button)
        self.layout.addWidget(self.remove_task_button)

        self.setCentralWidget(self.central_widget)

        self.setWindowTitle('Task Manager')
        self.setGeometry(100, 100, 1250, 600)

    def add_task(self):
        task_name = self.task_name_input.text()
        priority = self.priority_combobox.currentText()
        description = self.task_description_input.toPlainText()
        due_date = self.due_date_input.dateTime().toString("yyyy-MM-dd hh:mm:ss")

        task = Task(task_name, priority, description, due_date)
        self.priority_queue.push(task)

        print("Task Added:", task.name, "| Priority:", task.priority)

        self.refresh_task_table()

        self.task_name_input.clear()
        self.task_description_input.clear()

    def remove_task(self):
        removed_task = self.priority_queue.pop()

        if removed_task:
            print("Removed Task:", removed_task.name, "| Priority:", removed_task.priority)

            self.refresh_task_table()

    def view_task_details(self, row, column):
        task = self.priority_queue.heap[row]
        details_dialog = TaskDetailsDialog(task, self)
        details_dialog.exec_()

    def mark_task_completed(self, row, column):
        task = self.priority_queue.heap[row]
        task.completed = True
        print("Marked Task Completed:", task.name)

        self.refresh_task_table()

    def refresh_task_table(self):
        self.task_table.clearContents()
        for i, task in enumerate(self.priority_queue.heap):
            self.task_table.insertRow(i)
            self.task_table.setItem(i, 0, QTableWidgetItem(task.name))
            self.task_table.setItem(i, 1, QTableWidgetItem(task.priority))
            self.task_table.setItem(i, 2, QTableWidgetItem(task.description))
            self.task_table.setItem(i, 3, QTableWidgetItem(task.due_date))
            self.task_table.setItem(i, 4, QTableWidgetItem('Yes' if task.completed else 'No'))

            view_details_button = QPushButton('View Details')
            view_details_button.clicked.connect(lambda _, i=i: self.view_task_details(i, 0))
            mark_completed_button = QPushButton('Mark Completed')
            mark_completed_button.clicked.connect(lambda _, i=i: self.mark_task_completed(i, 0))

            self.task_table.setCellWidget(i, 5, view_details_button)
            if not task.completed:
                self.task_table.setCellWidget(i, 6, mark_completed_button)

        self.task_table.cellClicked.connect(self.view_task_details)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    task_app = TaskManagementApp()
    task_app.show()
    sys.exit(app.exec_())
