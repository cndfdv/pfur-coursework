package lab3.queue;

public class LabQueue {

    private QueueElement firstElement;
    private QueueElement lastElement;

    public void push(int el) {
        QueueElement newElement = new QueueElement(el);

        if (firstElement == null) {
            firstElement = newElement;
            lastElement = newElement;
        } else {
            lastElement.setNext(newElement);
            lastElement = newElement;
        }
    }

    public int pop() {
        if (firstElement == null) {
//            return 0;
            throw new RuntimeException("no elements in queue");
        } else {
            int retVal = firstElement.getValue();
            firstElement = firstElement.getNext();

            if (firstElement == null) {
                lastElement = null;
            }

            return retVal;
        }
    }
}
