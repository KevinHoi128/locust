import time
import unittest

from locust.dispatch import (
    all_users_have_been_dispatched,
    all_users_of_current_class_have_been_dispatched,
    balance_users_among_workers,
    dispatch_users,
    number_of_users_left_to_dispatch,
)
from locust.runners import WorkerNode


class TestBalanceUsersAmongWorkers(unittest.TestCase):
    def test_balance_users_among_1_worker(self):
        worker_node1 = WorkerNode("1")

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 3, "User2": 3, "User3": 3}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 5, "User2": 4, "User3": 2},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 5, "User2": 4, "User3": 2}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 1, "User2": 1, "User3": 1},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 1, "User2": 1, "User3": 1}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 1, "User2": 1, "User3": 0},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 1, "User2": 1, "User3": 0}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 0, "User2": 0, "User3": 0},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 0, "User2": 0, "User3": 0}})

    def test_balance_users_among_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 5, "User2": 4, "User3": 2},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 2, "User3": 1},
            "2": {"User1": 2, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 1, "User2": 1, "User3": 1},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 1, "User2": 1, "User3": 0},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 0, "User2": 0, "User3": 0},
        )
        expected_balanced_users = {
            "1": {"User1": 0, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)


class TestDispatchUsersWithWorkersWithoutPriorUsers(unittest.TestCase):
    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_15(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.15,
        )

        sleep_time = 1 / 0.15

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2_4(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2.4,
        )

        sleep_time = 2 / 2.4

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)


class TestDispatchUsersToWorkersHavingLessUsersThanTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_15(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.15,
        )

        sleep_time = 1 / 0.15

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2.4,
        )

        sleep_time = 2 / 2.4

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)


class TestDispatchUsersToWorkersHavingLessAndMoreUsersThanTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_15(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.15,
        )

        sleep_time = 1 / 0.15

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(1.98 <= delta <= 2.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0.98 <= delta <= 1.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2.4,
        )

        sleep_time = 2 / 2.4

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)


class TestDispatchUsersToWorkersHavingMoreUsersThanTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {"User3": 15}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        for spawn_rate in [0.15, 0.5, 1, 2, 2.4, 3, 4, 9]:
            users_dispatcher = dispatch_users(
                worker_nodes=[worker_node1, worker_node2, worker_node3],
                user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
                spawn_rate=spawn_rate,
            )

            ts = time.time()
            self.assertDictEqual(
                next(users_dispatcher),
                {
                    "1": {"User1": 1, "User2": 1, "User3": 1},
                    "2": {"User1": 1, "User2": 1, "User3": 1},
                    "3": {"User1": 1, "User2": 1, "User3": 1},
                },
            )
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.02, delta)

            ts = time.time()
            self.assertRaises(StopIteration, lambda: next(users_dispatcher))
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.02, delta)


class TestDispatchUsersToWorkersHavingTheSameUsersAsTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {"User1": 1, "User2": 1, "User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1, "User2": 1, "User3": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User1": 1, "User2": 1, "User3": 1}

        for spawn_rate in [0.15, 0.5, 1, 2, 2.4, 3, 4, 9]:
            users_dispatcher = dispatch_users(
                worker_nodes=[worker_node1, worker_node2, worker_node3],
                user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
                spawn_rate=spawn_rate,
            )

            ts = time.time()
            self.assertDictEqual(
                next(users_dispatcher),
                {
                    "1": {"User1": 1, "User2": 1, "User3": 1},
                    "2": {"User1": 1, "User2": 1, "User3": 1},
                    "3": {"User1": 1, "User2": 1, "User3": 1},
                },
            )
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.02, delta)

            ts = time.time()
            self.assertRaises(StopIteration, lambda: next(users_dispatcher))
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.02, delta)


class TestNumberOfUsersLeftToDispatch(unittest.TestCase):
    def test_number_of_users_left_to_dispatch(self):
        user_class_occurrences = {"User1": 6, "User2": 2, "User3": 8}
        balanced_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }

        dispatched_users = {
            "Worker1": {"User1": 5, "User2": 2, "User3": 6},
            "Worker2": {"User1": 5, "User2": 2, "User3": 6},
        }
        result = number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_class_occurrences)
        self.assertEqual(0, result)

        dispatched_users = {
            "Worker1": {"User1": 2, "User2": 0, "User3": 4},
            "Worker2": {"User1": 2, "User2": 0, "User3": 4},
        }
        result = number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_class_occurrences)
        self.assertEqual(4, result)

        dispatched_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 0, "User3": 4},
        }
        result = number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_class_occurrences)
        self.assertEqual(1, result)

        dispatched_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }
        result = number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_class_occurrences)
        self.assertEqual(0, result)


class AllUsersHaveBeenDispatched(unittest.TestCase):
    def test_all_users_have_been_dispatched(self):
        user_class_occurrences = {"User1": 6, "User2": 2, "User3": 8}
        effective_balanced_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }

        dispatched_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }
        self.assertTrue(
            all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences)
        )

        dispatched_users = {
            "Worker1": {"User1": 4, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }
        self.assertTrue(
            all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences)
        )

        dispatched_users = {
            "Worker1": {"User1": 2, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }
        self.assertFalse(
            all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences)
        )

        dispatched_users = {
            "Worker1": {"User1": 0, "User2": 0, "User3": 0},
            "Worker2": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertFalse(
            all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences)
        )

        dispatched_users = {
            "Worker1": {"User1": 4, "User2": 0, "User3": 0},
            "Worker2": {"User1": 4, "User2": 0, "User3": 0},
        }
        self.assertFalse(
            all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences)
        )


class TestAllUsersOfCurrentClassHaveBeenDispatched(unittest.TestCase):
    def test_all_users_of_current_class_have_been_dispatched(self):
        effective_balanced_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }

        dispatched_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User1")
        )
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User2")
        )
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User3")
        )

        dispatched_users = {
            "Worker1": {"User1": 4, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User1")
        )
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User2")
        )
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User3")
        )

        dispatched_users = {
            "Worker1": {"User1": 2, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }
        self.assertFalse(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User1")
        )
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User2")
        )
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User3")
        )

        dispatched_users = {
            "Worker1": {"User1": 0, "User2": 0, "User3": 0},
            "Worker2": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertFalse(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User1")
        )
        self.assertFalse(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User2")
        )
        self.assertFalse(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User3")
        )

        dispatched_users = {
            "Worker1": {"User1": 4, "User2": 0, "User3": 0},
            "Worker2": {"User1": 4, "User2": 0, "User3": 0},
        }
        self.assertTrue(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User1")
        )
        self.assertFalse(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User2")
        )
        self.assertFalse(
            all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, "User3")
        )
