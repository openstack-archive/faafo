from kombu import Exchange, Queue

task_exchange = Exchange('tasks', type='direct')
task_queues = [Queue('normal', task_exchange, routing_key='normal')]
