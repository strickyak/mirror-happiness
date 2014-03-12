# $ python  happy.py 'define incr 1 adding '  ' 3 9 adding incr '
#
# $ python  happy.py 'define incr: 1 adding.' 'define double: duplicating adding.' '3 double 9 double adding incr'
# >>>[25.0]

import re
import sys

NONALFA = re.compile('[^A-Za-z0-9]+')
NUMBER = re.compile('^[0-9]+([.][0-9]+)?$')

STOPS = set(['', 'the', 'a', 'an', 'number'])

ORDINALS = dict(
  first=1, second=2, third=3, fourth=4, fifth=5,
  sixth=6, seventh=7, eighth=8, nineth=9, tenth=10,
  eleventh=11, twelvth=12,
)

class Happy(object):

  def __init__(self):
    self.stack = []

  def Do(self, s):
    s = NONALFA.sub(' ', s)
    s = s.lower()
    ww = [x for x in s.split(' ') if x not in STOPS]
    if len(ww) > 1 and ww[0]=='define':
      setattr(self, ww[1], lambda: self.Eval(ww[2:]))
      return None
    elif len(ww) > 1 and ww[0]=='must':
      want = float(ww[1])
      self.stack = []
      self.Eval(ww[2:])
      if len(self.stack) != 1:
        raise Exception('Stack length: wnat 1 got %d ---- %s' % (len(self.stack), self.stack))
      got = float(self.stack[-1])
      if want != got:
        raise Exception('"must" Failed: want %s got %s' % (want, got))
      return None
    else:
      self.stack = []
      self.Eval(ww)
      return self.stack

  def Eval(self, ww):
    i = 0
    while i < len(ww):
      w = ww[i]
      print '<<< <<< <<<' + repr(w)
      if type(w) != str:
        self.stack.append(w)
      elif NUMBER.match(w):
        self.stack.append(float(w))
      elif w == 'opening':
        vecs = [ [] ]
        i+=1
        while i < len(ww):
          w = ww[i]
          if w == 'closing':
            if len(vecs) < 2:
              # finish the loop.
              break
            else:
              tmp = vecs.pop()
              vecs[-1].append(tmp)
          elif w == 'opening':
            vecs.append([])
          else:
            vecs[-1].append(w)
          i+=1
        self.stack.append(vecs[0])
      else:
        # Ordinals are special; they append to previous word.
        # i.e. "foo second" becomes "foo2".
        if i+1 < len(ww) and ww[i+1] in ORDINALS:
          i+=1
          w += ORDINALS[ww[i]]

        f = getattr(self, w, None)
        if not f:
          raise Exception('Unknown word: %s' % w)
        f()
      print '>>> >>> >>>' + repr(self.stack)
      i+=1


  def BinaryOp(self, op):
    x = self.stack.pop()
    y = self.stack.pop()
    self.stack.append(self.Binop(y, x, op))

  def Binop(self, y, x, op):
    if type(y) == list:
      if type(x) == list:
        if len(y) != len(x):
          raise Exception("Binop with differnt len lists: %d vs %d" % (len(y), len(x)))
        return [this.Binop(y1, x1, op) for y1, x1 in zip(y, x)]
      else:
        return [this.Binop(y1, x, op) for y1 in y]
    elif type(x) == list:
        return [this.Binop(y, x1, op) for x1 in x]
    else:
      return op(y, x)

  def adding(self):
    self.BinaryOp(lambda y, x: y + x)

  def subtracting(self):
    self.BinaryOp(lambda y, x: y - x)

  def multiplying(self):
    self.BinaryOp(lambda y, x: y * x)

  def dividing(self):
    self.BinaryOp(lambda y, x: y / x)

  def duplicating(self):
    self.stack.append(self.stack[-1])

  def sizing(self):
    tmp = self.stack.pop()
    self.stack.append(len(tmp))

  def choosing(self):
    t1 = self.stack.pop()
    t2 = self.stack.pop()
    self.stack.append(t2[int(t1)])

# TESTS
t = Happy()
t.Do('define incr: 1 adding.')
t.Do('must 8: 7 incr')
t.Do('define double: duplicating adding.')
t.Do('must 88: 44 double')
t.Do('must 25: 3 double 9 double adding incr')
t.Do('must 3: opening 44 55 66 closing sizing')
t.Do('must 55: opening 44 55 66 closing 1 choosing')
t.Do('must 2: opening 44 opening 22 33 closing 66 closing 1 choosing sizing')
t.Do('must 22: opening 44 opening 22 33 closing 66 closing 1 choosing 0 choosing')


# MAIN
if __name__ == '__main__':
  h = Happy()
  for a in sys.argv[1:]:
    print '<<<' + repr(a)
    print '>>>' + repr(h.Do(a))
