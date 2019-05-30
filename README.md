Reify
===
### A Templating Language for Find-And-Replace

## Introduction

Reify is a lightweight templating engine built on regular expressions 
intended for finding and replacing complicated patterns in documents.
The original intended use-case for Reify is for mass-editing repetitive,
bad/messy HTML and XML markup, usually that generated by a computer, but
it will work in any document.

## Templating Language

### Two Kinds of Templates
There are two slightly different variants of Reify: one for patterns
that are to be searched for in a document and one for patterns that are
supposed to replace the original one. For the sake of simplicity, the
former shall be called the "input template" and the latter will be the
"output template"

### Slots
A "slot" is a placeholder for some data. In an input template, a slot
represents some data in the original document; in an output document, it
represents a place where data from the original document should be put.
All slots consist of some text in double braces: `{{...}}`.
The main difference between an input template and an output template is
the kinds of slots each of them can use. 

The first kind of slot is a wildcard slot, which is just `{{}}`. It can
only appear in an input template and it represents data in the document
that might be used when during the reformatting. These are automatically
numbered in the order they appear and they can be referenced by number
in the output template. Say you are trying to render an item in an RSS
feed as an anchor tag in HTML. You may do it like:

```xml
<!-- INPUT -->
<item>
    <title>{{}}</title>
    <link>{{}}</link>
    <description>{{}}</description>
</item>
```

```html
<!-- OUTPUT -->
<a href="{{2}}" title="{{3}}">{{1}}</a>
```

For your own sanity, if you choose to go this route, you may want to
write the numbers in the input template slots. This won't affect the
way Reify actually numbers the slots, but it saves a bit of headache.

Still, a numbering scheme can get difficult and inconvenient. This is
why you are also allowed to use labels. A label can contain letters,
numbers, hyphens, or underscores. The number reminders you can write in
the slots are also labels. Labelled slots can still be referenced by
number.

Updating the RSS example above to use labels:

```xml
<!-- INPUT -->
<item>
    <title>{{title}}</title>
    <link>{{link}}</link>
    <description>{{desc}}</description>
</item>
```

```html
<!-- OUTPUT -->
<a href="{{link}}" title="{{desc}}">{{title}}</a>
```

If there's any information you don't plan on using, but that doesn't fit
an easy pattern (such as a UUID string or a hash or a randomly generated
string), you can use a null slot, `{{:}}`, to say "there is *some* data
here, but it isn't important". It's equivalent to `(?:.*)` in regex. Of
course, a null slot can only be placed in an input template.

In the output template, there are a few shorthands you can use to place
slot data consecutively. You can place multiple labels or numbers into
the same slot as a space-separated list. This is good if, for example,
you have HTML with a lot of useless `<span>` elements.

```html
<!-- INPUT -->
<div>
    <span class="author">{{author}}</span>
    <span class="title">{{title}}</span>
    <span class="year">{{year}}</span>
</div>
```

```html
<!-- OUTPUT -->
<div class="citation">{{author title year}}</div>
```

If you are using numbers, you can even use ranges:

```html
<!-- OUTPUT -->
<div class="citation">{{1..3}}</div>
```

Note that ranges are inclusive of both bounds.

## Command Line Interface

The Reify command line tool, `reify`, allows you to compile regular
expressions from Reify templates, find patterns in a file matching a
template, and perform find-and-replace on whole documents. These three
functions correspond to three commands: `generate`, `find`, and `subs`,
respectively.

### `subs`
Perhaps the most useful command is `reify subs`. This is a powerful
find-and-replace tool that will search in a document for patterns 
matching an input template and replaces them with the output template.
By default it just prints out the reformatted document, but it can be
redirected to another file or the substitution can be done in-place. It
takes the following arguments:

- `-it` or `--input-template`: Path to the template you want to replace
- `-ot` or `--output-template`: Path to the template you want to replace
the old pattern with
- `-f` or `--file`: Path to the file you want to perform find-and-replace
on

And it can take the following flags:

- `-W` or `--compress-whitespace`: Replaces all newlines and series of
2 or more whitespace characters with `\s*` (variable number of any
whitespace) in an input template. It's recommended if you have messy or 
minified markup, or markup generated by an algorithm or server.
- `-I` or `--in-place`: Performs the substitution in-place, meaning that
the original document will be edited to have all occurrences of the
input template replaced with the output template.

### `generate`
The command `reify generate` allows you to compile Reify templates into
regular expression syntax. This can help if you want to use your own
find-and-replace tool, or if you just need to generate a complicated
regex for a program. It takes the following arguments:

- `-it` or `--input-template`: Path to input template
- `-ot` or `--output-template`: Path to output template

It can also take the following flags:

- `-W` or `--compress-whitespace`: Does the same thing it does for `subs`

### `find`
`reify find` will take an input template and find all occurrences of 
that template in a file. All matches will be printed out in the terminal
with the data from the slots highlighted in green. This is useful for 
testing templates. It takes the following arguments:

- `-t` or `--template`: Path to the template you want to search against
- `-f` or `--file`: Path to the file you want to search in

And it can take the following flags:

- `-W` or `--compress-whitespace`: Does the same thing it does for `subs`
and `generate`

## Todo
1. Add a graphical user interface.
1. Create a proper API so it can be more readily employed in other
applications.
1. Maybe make the parsing algorithm a *bit* more sophisticated
1. Make it more fully-featured. Currently it applies to only a few
narrow use-cases and can't do nearly as much as regex can.

## License
Copyright &copy; 2019 Aidan T. Manning

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

