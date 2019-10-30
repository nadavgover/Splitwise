class Link:
    def __init__(self, val, next_link, prev_link):
        self.val = val
        self.next_link = next_link
        self.prev_link = prev_link


class LinkedList:

    def __init__(self):
        self.head, self.last = None, None
        self.size = 0

    def insert_last(self, x):
        """Adds x as the last link of the linked list"""
        new_link = Link(x, None, self.last)  # Make a new link
        if self.size == 0:
            self.head = new_link
        else:
            self.last.next_link = new_link

        self.last = new_link
        self.size += 1

    def insert_first(self, x):
        """Adds x at the front of the linked list"""
        new_link = Link(x, self.head, None)  # Make a new link
        if self.size == 0:
            self.last = new_link
        else:
            self.head.prev_link = new_link

        self.head = new_link
        self.size += 1

    def remove_first(self):
        """Removes the first link and returns it"""
        if self.size == 0:
            return None

        head = self.head.val
        if self.size == 1:  # only one element in the list, so after removal the list is empty
            self.head = None
            self.last = None
        else:  # more than one element, than update the first link
            self.head = self.head.next_link
            self.head.prev_link = None

        self.size -= 1
        return head

    def remove_last(self):
        """Removes the last link and returns it"""
        if self.size == 0:
            return None

        last = self.last.val
        if self.size == 1:  # only one element in the list, so after removal the list is empty
            self.head = None
            self.last = None
        else:  # more than one element, than update the last link
            self.last = self.last.prev_link
            self.last.next_link = None

        self.size -= 1
        return last

    def __len__(self):
        return self.size

    def __str__(self):
        output = ""
        if self.head is None:  # if the list is empty
            return output

        output += str(self.head.val)
        current_link = self.head.next_link
        while current_link is not None:
            output += ", " + str(current_link.val)
            current_link = current_link.next_link
        return output


class Queue:
    def __init__(self):
        self.linked_list = LinkedList()

    def enqueue(self, x):
        self.linked_list.insert_last(x)

    def dequeue(self):
        return self.linked_list.remove_first()

    def is_empty(self):
        return len(self.linked_list) == 0

    def front(self):
        """Returns the first item and does not dequeue it"""
        if len(self.linked_list) > 0:
            return self.linked_list.head.val

    def __contains__(self, item):
        if len(self.linked_list) > 0:
            current = self.linked_list.head
            if current.val == item:
                return True
            while current.next_link is not None:
                current = current.next_link
                if current.val == item:
                    return True

        return False

    def __len__(self):
        return len(self.linked_list)

    def __str__(self):
        return self.linked_list.__str__()