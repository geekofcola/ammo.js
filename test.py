import os, sys, re, json
from subprocess import Popen, PIPE, STDOUT

# By default use builds/ammo.js. Or the commandline argument can override that.
build = os.path.join('builds', 'ammo.js')
if len(sys.argv) > 1:
  build = sys.argv[1]
print 'Using build:', build
build = os.path.basename(build)

exec(open(os.path.expanduser('~/.emscripten'), 'r').read())

if SPIDERMONKEY_ENGINE:
  JS_ENGINE = SPIDERMONKEY_ENGINE
elif V8_ENGINE:
  JS_ENGINE = V8_ENGINE # Note: fails stress due to floating point differences
else:
  JS_ENGINE = NODE_JS
if type(JS_ENGINE) == str:
  JS_ENGINE = [JS_ENGINE]


print
print '==================================='
print JS_ENGINE
print '==================================='
print

def run(filename):
  filename = os.path.abspath(filename)
  test_utils = os.path.abspath(os.path.join('tests', 'testutils.js'))
  old = os.getcwd()
  try:
    os.chdir('builds')
    if JS_ENGINE == SPIDERMONKEY_ENGINE:
      cmd = JS_ENGINE + ['-e', 'gcparam("maxBytes", 1024*1024*1024); load("' + build + '"); load("' + test_utils + '")', filename]
    else:
      with open('t.js', 'w') as f:
        f.write(open(build).read())
        f.write(open(test_utils).read())
        f.write(open(filename).read())
      cmd = JS_ENGINE + ['t.js']
    print(' '.join(cmd), 'in', os.getcwd())
    return Popen(cmd, stdout=PIPE).communicate()[0]
  finally:
    os.chdir(old)

__counter = 0
def stage(text):
  global __counter
  print __counter, ':', text
  __counter += 1

if len(sys.argv) != 3 or sys.argv[2] != 'benchmark':
  stage('regression tests')

  for test in ['basics', 'wrapping', '2', '3', 'constraint', 'compoundShape']:
    name = test + '.js'
    print '     ', name
    fullname = os.path.join('tests', name)
    output = run(fullname)
    assert 'ok.' in output, output

  stage('hello world')

  output = run(os.path.join('examples', 'hello_world.js'))
  #assert open(os.path.join('examples', 'hello_world.txt')).read() in output, output
  assert 'ok.' in output, output

stage('stress')

output = run(os.path.join('tests', 'stress.js'))
#assert
'''
0 : 0.00,-56.00,0.00
1 : 13.03,-5.00,-5.24
2 : 2.43,-5.00,-3.49
3 : -6.77,-5.54,-0.77
4 : -2.55,-5.00,2.84
5 : 11.75,-5.00,11.25
6 : 2.35,-5.61,0.12
total time:''' in output#, output
assert 'ok.' in output, output
print '   stress benchmark: ' + output.split('\n')[-3]

print
print '==================================='
print
print 'ok.'

