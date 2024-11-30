
import json
import subprocess
import sys

from litellm import completion

P_SYS = '''
Emit only a single JSON object containing the key `context` with python code to run as context and `deps` with a list of python packages that need to be installed.
Do not emit any other text.
'''

P_USER = '''
The current code context is:
```
{context}
```

We need to execute the following user code:
```
{code}
```

Currently it fails with this exception:
```
{exception}
```

Please emit a JSON object containing the new context (keyed by `context`) and a list of required packages to install (keyed by `deps`).
If you need to redefine classes, please try to do so in a backwards compatible way as much as possible.
If you need to, feel free to import other libraries at the top of the new context, but do so sparingly.
Note that we are running this code inside a jupyter notebook.
Do not attempt to fix or rewrite any of the user code; you can only change the context code.
'''

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL)

class Omni:
    def __init__(self, model='anthropic/claude-3-5-sonnet-20241022', allow_install=False):
        self.context = ''
        self.model = model
        self.allow_install = allow_install

    def fixup(self, code, exception, verbose=False):
        messages = [
            {"role": "system", "content": P_SYS},
            {"role": "user", "content": P_USER.format(context=self.context, code=code, exception=exception)},
        ]
        c = completion(self.model, messages)
        m = c.choices[0].message.content

        try:
            p = json.loads(m)
            
            if 'context' in p:
                if verbose:
                    print('[FIX]')
                    print(p['context'])
                self.context = p['context']
            if 'deps' in p:
                if self.allow_install:
                    for d in p['deps']:
                        try:
                            if verbose:
                                print('[INSTALL]', d)
                            install(d)
                        except:
                            pass
            return True
        except:
            print('[ERROR] Failed to parse LLM response as JSON')
            print(m)
            raise Exception('Failed to parse LLM response as JSON')

    def execute(self, code, verbose=False):
        retry = True
        last = None
        while retry:
            try:
                g = {}
                exec(self.context, g, g)
                exec(code, g, g)
                retry = False
            except Exception as e:
                if repr(e) == last:
                    raise Exception('Bailing due to error loop')
                last = repr(e)
                if verbose:
                    print('[FAIL]', repr(e))
                if not self.fixup(code, repr(e), verbose):
                    retry = False
