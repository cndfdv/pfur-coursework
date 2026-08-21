package lab3.sort;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class LarSorterTest {


    @Test
    public void test() {

        int[] sourceArray = new int[]{5, 8, 3, 2, 97, 23, 56, 12, 7, 44, 22};

        int[] result = new LabSorter().sort(sourceArray);

        Assertions.assertNotNull(result);

        int lastElement = Integer.MIN_VALUE;
        for (int i = 0; i < result.length; i++) {
            Assertions.assertTrue(lastElement < result[i]);
            lastElement = result[i];
        }
    }
}
