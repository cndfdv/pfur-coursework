package lab3.stack;

/**
 * Класс, представляющий структуру данных "Стек"
 */
public class LabStack {
    /**
     * Следующий элемент стека
     */
    private StackElement next;

    /**
     * Метод для помещения элемента в стек
     *
     * @param elem элемент, который необходимо поместить в стек
     */
    public void push(String elem) {
        StackElement newElement = new StackElement(elem);

        if (next == null) {
            next = newElement;
        }
        else {
            newElement.setNext(next);
            next = newElement;
        }
    }

    /**
     * Метод для вытаскивания элемента из стека. Если стек пуст - возвращает null
     *
     * @return следующий элемент стека
     */
    public String pop() {
        if (next == null){
            return null;
        }
        else {
            String poppedValue = next.getValue();
            next = next.getNext();

            return poppedValue;
        }
    }
}
