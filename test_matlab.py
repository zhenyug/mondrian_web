import matlab.engine
import time
t0 = time.time()
eng = matlab.engine.start_matlab()
eng.addpath('~/Documents/mondrian/src_matlab/')
t1 = time.time()
result = eng.exp_test('data/im_1.jpg')
t2 = time.time()
print 'it took {} seconds to start matlab'.format(t1-t0)
print 'it took {} seconds to finish classification'.format(t2-t1)

result = eng.exp_test('data/im_1.jpg')
t3 = time.time()
print 'it took {} seconds to finish classification'.format(t3-t2)
print result
eng.quit()