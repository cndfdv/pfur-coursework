package lab3.stack;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class LabStackTest {

    @Test
    public void test() {
        LabStack stack = new LabStack();

        String[] sourceElementsArray = new String[]{"Moscow", "Paris", "London", "New York", "Berlin", "Madrid"};

        for (String i : sourceElementsArray) {
            stack.push(i);
        }

        for (int i = sourceElementsArray.length - 1; i >= 0; i--) {
            Assertions.assertEquals(sourceElementsArray[i], stack.pop());
        }

        Assertions.assertNull(stack.pop());
    }
}
