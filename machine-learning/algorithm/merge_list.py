class Solution:

    def Merge(self, pHead1, pHead2):
        if pHead1 is None: return pHead2
        if pHead2 is None: return pHead1

        if pHead1.val < pHead2.val:
            pHead1.next = self.Merge(pHead1.next, pHead2)
            head = pHead1
        else:
            pHead2.next = self.Merge(pHead1, pHead2.next)
            head = pHead2
        return head
