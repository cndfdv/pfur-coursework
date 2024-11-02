package lab3.sort;

public class LabSorter {

    /**
     * Метод для сортировки массива целых чисел.
     *
     * @param source исходный массив для сортировки.
     */
    public int[] sort(int[] source) {
        int n = source.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - 1 - i; j++) {
                if (source[j] > source[j + 1]) {
                    int b = source[j];
                    source[j] = source[j + 1];
                    source[j + 1] = b;
                }
            }
        }
        return source;
    }
}
