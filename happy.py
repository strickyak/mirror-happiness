# $ python  happy.py 'define incr 1 adding '  ' 3 9 adding incr '
#
# $ python  happy.py 'define incr: 1 adding.' 'define double: duplicating adding.' '3 double 9 double adding incr'
# >>>[25.0]

import re
import sys

NONALFA = re.compile('[^A-Za-z0-9]+')
NUMBER = re.compile('^[0-9]+([.][0-9]+)?$')

STOPS = set(['', 'the', 'a', 'an', 'number'])

class Happy(object):

  def __init__(self):
    self.stack = []
    self.words = dict(
        adding=self.adding,
        subtracting=self.subtracting,
        multiplying=self.multiplying,
        dividing=self.dividing,
        duplicating=self.duplicating,
    )

  def Do(self, s):
    s = NONALFA.sub(' ', s)
    s = s.lower()
    ww = [x for x in s.split(' ') if x not in STOPS]
    if len(ww) > 1 and ww[0]=='define':
      self.words[ww[1]] = lambda: self.Eval(ww[2:])
      return None
    else:
      self.Eval(ww)
      return self.stack

  def Eval(self, ww):
    i = 0
    while i < len(ww):
      w = ww[i]
      print '<<< <<< <<<' + repr(w)
      if NUMBER.match(w):
        self.stack.append(float(w))
      else:
        f = self.words.get(w)
	if not f:
          raise Exception('Unknown word: %s' % w)
	f()
      print '>>> >>> >>>' + repr(self.stack)
      i+=1


  def binaryOp(self, op):
    x = self.stack.pop()
    y = self.stack.pop()
    self.stack.append(self.binop(y, x, op))

  def binop(self, y, x, op):
    if type(y) == list:
      if type(x) == list:
        if len(y) != len(x):
	  raise Exception("binop with differnt len lists: %d vs %d" % (len(y), len(x)))
        return [op(y1, x1) for y1, x1 in zip(y, x)]
      else:
        return [op(y1, x) for y1 in y]
    elif type(x) == list:
        return [op(y, x1) for x1 in x]
    else:
      return op(y, x)

  def adding(self):
    self.binaryOp(lambda y, x: y + x)

  def subtracting(self):
    self.binaryOp(lambda y, x: y - x)

  def multiplying(self):
    self.binaryOp(lambda y, x: y * x)

  def dividing(self):
    self.binaryOp(lambda y, x: y / x)

  def duplicating(self):
    self.stack.append(self.stack[-1])

if __name__ == '__main__':
  h = Happy()
  for a in sys.argv[1:]:
    print '<<<' + repr(a)
    print '>>>' + repr(h.Do(a))
