package lab3.queue;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class LabQueueTest {

    @Test
    public void test() {
        LabQueue queue = new LabQueue();

        int[] sourceElementsArray = new int[]{456, 34, 467, 67877, 7890, 22, 42};

        for (int i : sourceElementsArray) {
            queue.push(i);
        }

        for (int i : sourceElementsArray) {
            Assertions.assertEquals(i, queue.pop());
        }

        RuntimeException thrown = Assertions.assertThrows(
                RuntimeException.class,
                () -> queue.pop(),
                "Expected queue.pop() to throw, but it didn't"
        );

        Assertions.assertTrue(thrown.getMessage().contains("no elements in queue"));
    }
}
