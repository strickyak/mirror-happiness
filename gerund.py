# Gerund: a joyful language for speech dictation.
#
# Voice dictation seems to work well on gerunds,
# so most builtin words end in -ing.
#
# $ python  gerund.py 'define incr 1 adding '  ' 3 9 adding incr '
#
# $ python  gerund.py 'define incr: 1 adding.' 'define double: duplicating adding.' '3 double 9 double adding incr'
# >>>[25.0]

import re
import sys

NONALFA = re.compile('[^A-Za-z0-9]+')
NUMBER = re.compile('^[0-9]+([.][0-9]+)?$')

STOPS = set(['', 'the', 'a', 'an', 'number'])

ORDINALS = dict(
  first=1, second=2, third=3, fourth=4, forth=4, fifth=5,
  sixth=6, seventh=7, eighth=8, nineth=9, tenth=10,
  eleventh=11, twelvth=12,
)

class Gerund(object):

  def __init__(self):
    self.stack = []

  def Run(self, s):
    s = NONALFA.sub(' ', s)
    s = s.lower()
    ww = [x for x in s.split(' ') if x not in STOPS]
    if len(ww) > 1 and ww[0]=='define':
      setattr(self, ww[1], lambda: self.Eval(self.Compile(ww[2:])))
      return None
    elif len(ww) > 1 and ww[0]=='must':
      want = float(ww[1])
      self.stack = []
      self.Eval(self.Compile(ww[2:]))
      if len(self.stack) != 1:
        raise Exception('Stack length: want 1 got %d ---- %s' % (len(self.stack), self.stack))
      got = float(self.stack[-1])
      if want != got:
        raise Exception('"must" Failed: want %s got %s' % (want, got))
      return None
    else:
      self.stack = []
      self.Eval(self.Compile(ww))
      return self.stack

  def Compile(self, ww):
    z = []
    i = 0
    while i < len(ww):
      w = ww[i]
      print '<<< <<< <<<' + repr(w)
      if type(w) != str:
        z.append(w)
      elif NUMBER.match(w):
        z.append(float(w))
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
              vecs[-1].append(self.Compile(tmp))
          elif w == 'opening':
            vecs.append([])
          else:
            vecs[-1].append(w)
          i+=1
        z.append(self.Compile(vecs[0]))
      else:
        # Ordinals are special; they append to previous word.
        # i.e. "foo second" becomes "foo2".
        if i+1 < len(ww) and ww[i+1] in ORDINALS:
          i+=1
          w += str(ORDINALS[ww[i]])

        # Four prepositions can make compound words.
        if i+2 < len(ww) and ww[i+1] in ['from', 'of', 'for', 'with']:
          i+=2
          w += '_' + ww[i]

        # The word should be a method of self.
        print '=== word = ', w
        f = getattr(self, w, None)
        if not f:
          raise Exception('Unknown word: %s' % w)
        z.append(f)
      print '>>> >>> >>>' + repr(self.stack)
      i+=1
    return z

  def Eval(self, ww):
    i = 0
    while i < len(ww):
      w = ww[i]
      print '<<< <<< <<<' + repr(w)
      if callable(w):
        w()
      else:
        # A literal.  Push it on the stack.
        self.stack.append(w)

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

  def choosing1(self):
    t = self.stack.pop()
    self.stack.append(t[0])
  def choosing2(self):
    t = self.stack.pop()
    self.stack.append(t[1])
  def choosing3(self):
    t = self.stack.pop()
    self.stack.append(t[2])
  def choosing4(self):
    t = self.stack.pop()
    self.stack.append(t[3])
  def choosing5(self):
    t = self.stack.pop()
    self.stack.append(t[4])

  def changing(self):
    t1 = self.stack.pop()
    t2 = self.stack.pop()
    t3 = self.stack.pop()
    t3[int(t2)] = t1

  def changing1(self):
    t1 = self.stack.pop()
    t3 = self.stack.pop()
    t3[0] = t1
  def changing2(self):
    t1 = self.stack.pop()
    t3 = self.stack.pop()
    t3[1] = t1
  def changing3(self):
    t1 = self.stack.pop()
    t3 = self.stack.pop()
    t3[2] = t1
  def changing4(self):
    t1 = self.stack.pop()
    t3 = self.stack.pop()
    t3[3] = t1
  def changing5(self):
    t1 = self.stack.pop()
    t3 = self.stack.pop()
    t3[4] = t1

  def getting1(self):
    self.stack.append(self.stack[-1])
  def getting2(self):
    self.stack.append(self.stack[-2])
  def getting3(self):
    self.stack.append(self.stack[-3])
  def getting4(self):
    self.stack.append(self.stack[-4])
  def getting5(self):
    self.stack.append(self.stack[-5])

  def putting1(self):
    t = self.stack.pop()
    self.stack[-1] = t
  def putting2(self):
    t = self.stack.pop()
    self.stack[-2] = t
  def putting3(self):
    t = self.stack.pop()
    self.stack[-3] = t
  def putting4(self):
    t = self.stack.pop()
    self.stack[-4] = t
  def putting5(self):
    t = self.stack.pop()
    self.stack[-5] = t

  def popping(self):
    self.stack.pop()
  def popping1(self):
    self.stack.pop()
  def popping2(self):
    self.stack.pop()
    self.stack.pop()
  def popping3(self):
    self.stack.pop()
    self.stack.pop()
    self.stack.pop()
  def popping4(self):
    self.stack.pop()
    self.stack.pop()
    self.stack.pop()
    self.stack.pop()
  def popping5(self):
    self.stack.pop()
    self.stack.pop()
    self.stack.pop()
    self.stack.pop()
    self.stack.pop()

  def running(self): # i
    t = self.stack.pop()
    self.Eval(t)

  def dipping(self): # dip
    t1 = self.stack.pop()
    t2 = self.stack.pop()
    self.Eval(t1)
    self.stack.append(t2)
  def dipping2(self): # dip2
    t1 = self.stack.pop()
    t2 = self.stack.pop()
    t3 = self.stack.pop()
    self.Eval(t1)
    self.stack.append(t3)
    self.stack.append(t2)
  def dipping3(self): # dip3
    t1 = self.stack.pop()
    t2 = self.stack.pop()
    t3 = self.stack.pop()
    t4 = self.stack.pop()
    self.Eval(t1)
    self.stack.append(t4)
    self.stack.append(t3)
    self.stack.append(t2)

# TESTS
t = Gerund()
t.Run('define incr: 1 adding.')
t.Run('must 8: 7 incr')
t.Run('define double: duplicating adding.')
t.Run('must 88: 44 double')
t.Run('must 25: 3 double 9 double adding incr')
t.Run('must 3: opening 44 55 66 closing sizing')
t.Run('must 55: opening 44 55 66 closing 1 choosing')

t.Run('must 2: opening 44 opening 22 33 closing 66 closing 1 choosing sizing')
t.Run('must 22: opening 44 opening 22 33 closing 66 closing 1 choosing 0 choosing')
t.Run('must 33: opening 44 opening 22 33 closing 66 closing choosing2 choosing2')

t.Run('must 33: 11 22 30 getting the third getting the third adding putting the third popping2')

t.Run('must 42: 10 opening 30 2 adding closing running adding')
t.Run('must 42: 10 opening 4 opening 5 3 adding closing running  multiplying closing running adding')
t.Run('must 42: 8 10 opening 4 multiplying closing dipping adding')
t.Run('must 42: 8 6 4 opening 4 multiplying closing dipping the second adding adding')
t.Run('must 42: 8 6 3 1 opening 4 multiplying closing dipping the third adding adding adding')

# MAIN
if __name__ == '__main__':
  h = Gerund()
  for a in sys.argv[1:]:
    print '<<<' + repr(a)
    print '>>>' + repr(h.Run(a))
