# OMNI

Generate an API on-the-fly with LLMs.

---

## Warning

This project will run arbitrary code from an LLM on your machine. If you don't want that to happen, don't install this project.

## Install

```
pip install omni-binding-api
```

## Usage

Create an `omni` context:
```py
from omni import Omni

o = Omni() # default is anthropic/claude-3-5-sonnet-20241022
```
or specify a particular model
```py
o = Omni(model='openai/gpt-4o')
```
then execute any code:
```py
o.execute('''
# any code here
''')
```
Make sure the associated API keys are set for the model you specify. See a list of available models here: https://docs.litellm.ai/docs/providers.


## Example 1

Suppose we want to draw some shapes in Jupyter notebook, but we don't know the right API. Let's just define our own on the fly!

Create an `omni` context:

```py
from omni import Omni

o = Omni()
```

Invoke _any_ Python code inside the omni context:
```py
o.execute('''
r = Rect(width=4, height=6)
r.set_origin(5, 4)
r.set_color('green')
r.set_rotation(deg=45)

c = Canvas()
c.add(r)
c.draw()
''')
```

Neither `Rect` or `Canvas` is defined, so `omni` will query an LLM to generate _binding_ code that does something plausible (here it decides to use `matplotlib`). Then it will rerun this code in that context, in this case successfully drawing and rendering a rectangle:

![r1](./assets/r1.png)

Now that we have _an_ implementation of `Rect` and `Canvas`, we can continue to use them:

```py
o.execute('''
r = Rect(width=4, height=6)
r.set_origin(5, 4)
r.set_color('green')
r.set_rotation(deg=45)

r2 = Rect(width=3, height=3)
r2.set_origin(2, 2)
r2.set_color('red')
r2.set_rotation(deg=10)

c = Canvas()
c.add(r)
c.add(r2)
c.draw()
''')
```

In this case, the new code did not throw an error. Since we already have a context for `Rect` and `Canvas`, we immediately get the following figure _without_ having to query the LLM again:

![r2](./assets/r2.png)

Let's draw a triangle now:

```py
o.execute('''
r = Rect(width=4, height=6)
r.set_origin(5, 4)
r.set_color('green')
r.set_rotation(deg=45)

r2 = Rect(width=3, height=3)
r2.set_origin(2, 2)
r2.set_color('red')
r2.set_rotation(deg=10)

t = Triangle(width=3, height=5)
t.set_origin(6,6)
t.set_color('blue')

c = Canvas()
c.add(r)
c.add(r2)
c.add(t)
c.draw()
''')
```

This invocation errors (`Triangle` is not defined), so we query the LLM to extend our API. Then it reruns and we get a nice triangle:

![r3](./assets/r3.png)

Now lets add random shapes by using the function `add_random_shapes` (which doesn't currently exist):

```py
o.execute('''
c = Canvas()
c.add_random_shapes(num=5)
c.draw()
''')
```

This hits the LLM to figure out what to do and we get:

![r4](./assets/r4.png)

Of course now we can scale up without needing to query the LLM:

```py
o.execute('''
c = Canvas()
c.add_random_shapes(num=100)
c.draw()
''')
```

![r5](./assets/r5.png)

Now let's make an animation and save it as a GIF. I have no idea how to do this so lets just create a new `Gif` object which we can add frames to, and assume the `Canvas` has some way to `.render` into something that can be added to a `Gif`:

```py
o.execute('''
g = Gif()

for i in range(10):
    c = Canvas()
    c.add_random_shapes(num=100)
    r = c.render()
    g.add_frame(r, ms=20)

g.save('./out.gif')
''')
```

This queries an LLM and we get back an implementation of these APIs that successfully does the thing:

![out.gif](./assets/out.gif)

## Example 2

Suppose we want to do some github exploration. I want to look at all the github repos I have and explore the data.

We'll create a new omni context:
```py
o2 = Omni()
```

Then use the api `fetch_github_projects` to get my projects:

```py
o2.execute('''
projects = fetch_github_projects(user='hgarrereyn')

for p in projects:
    print(f'{p.name} :: {p.stars}')
''')
```
```
2018submissions :: 0
AudioScroll-Extension :: 9
beam :: 0
bn-fish-disassembler :: 10
bn-pokemon-mini :: 9
bn-riscv-disassembler :: 2
bn-uxn :: 1
bn-wasm :: 9
BRCA1-BioAssay-Review :: 0
ChocolateFixGame :: 0
chromium :: 0
Clairvoyance :: 25
ctfblog :: 0
ctfdocker :: 0
curl :: 0
DataSort :: 0
dice-is-you :: 7
dicecraft :: 0
dicectf2022-breach :: 4
dicectf22-taxes :: 12
doppler :: 0
EasyCTF-2017-Write-ups :: 0
easyctf-2017-writeups :: 0
EconGame :: 0
format-string-attacks :: 0
fossasia.github.io :: 0
GeneralsIO-Bot-Controller :: 2
ghidra :: 0
gitbook-plugin-collapsible-chapters :: 0
GLaDOS :: 0
```

Very nice! But it looks like it didn't actually fetch them all (maybe due to pagination?). Let's explicitly add a `fetch_all=True` to our call:

```py
o2.execute('''
projects = fetch_github_projects(user='hgarrereyn', fetch_all=True)

for p in projects:
    print(f'{p.name} :: {p.stars}')
''')
```
```
2018submissions :: 0
AudioScroll-Extension :: 9
beam :: 0
bn-fish-disassembler :: 10
bn-pokemon-mini :: 9
bn-riscv-disassembler :: 2
bn-uxn :: 1
bn-wasm :: 9
BRCA1-BioAssay-Review :: 0
ChocolateFixGame :: 0
chromium :: 0
Clairvoyance :: 25
ctfblog :: 0
...
OCRaaP :: 123
omni :: 0
phenny :: 0
PittAPI :: 0
pwndbg :: 0
pyalgotrade :: 0
reddit :: 1
redpandacoin :: 0
SBVA :: 31
STRIDE :: 98
sugar :: 0
tfx-bsl :: 0
Th3g3ntl3man-CTF-Writeups :: 21
TIFF :: 0
```

Let's visualize this data:
```py
o2.execute('''
projects = fetch_github_projects(user='hgarrereyn', fetch_all=True)
plot_bar_chart(projects)
''')
```
![p1](./assets/p1.png)

Very nice, but a bit unreadable. Let's make it horizontal and also filter to the top 25, sorted by stars:
```py
o2.execute('''
projects = fetch_github_projects(user='hgarrereyn', fetch_all=True)
top = top_sorted(projects, num=25)
plot_bar_chart(top, vertical=False)
''')
```
![p2](./assets/p2.png)

Let's flip it the other way (adding `[::-1]`) and ask for a bit more pizazz with `with_pizazz=True`:

```py
o2.execute('''
projects = fetch_github_projects(user='hgarrereyn', fetch_all=True)
top = top_sorted(projects, num=25)[::-1]
plot_bar_chart(top, vertical=False, with_pizazz=True)
''')
```

![p3](./assets/p3.png)

Very nice! But suppose, we actually want to color the bars by the main language in the repo. Let's use the flag `colored_by_primary_language=True`:

```py
o2.execute('''
projects = fetch_github_projects(user='hgarrereyn', fetch_all=True)
top = top_sorted(projects, num=25)[::-1]
plot_bar_chart(top, vertical=False, colored_by_primary_language=True)
''')
```

![p4](./assets/p4.png)
