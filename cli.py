import click
from TemplateProcessor import *


@click.group("reify")
def reify():
    """The Reify Template Compiler

    Reify is a simple templating language that compiles to regular expression syntax to make finding
    and replacing complex patterns with other complex patterns less of a pain.

    The intended use-case of reify is to find and replace large amounts of repetitive (usually
    computer-generated) XML and HTML markup, while retaining whatever content the user wants.
    However it will work for arbitrary text documents.

    Here is a rundown of how the templating language works:

    The templates come in two variants: input and output. The input variant is for the markup
    that you want to replace, and the output variant is for the markup it should be replaced with.
    When you use reify to find-and-replace in a document, you have to provide it one of each variant.

    The reify compiler looks for "slots" between double-braces: {{...}}. In the input variant, a slot
    represents arbitrary data that exists in the document. In the output variant, it represents a
    place where data from the original document should be put. In the simplest case, you simply put an
    empty slot, {{}}, in the input variant, reify automatically numbers them in the order they appear,
    and then you reference the numbers in the output variant. For example, say you want to turn some
    XML into an anchor tag in HTML (like you're rendering an RSS feed). You could do this by:

    Input:

    <title>{{}}</title>
    <link>{{}}</link>

    Output:

    <a href="{{2}}">{{1}}</a>

    It's highly recommended that you label your slots. You could label them with a number (which will
    NOT have an effect on how the compiler numbers them internally, but rather gives them the label
    of _<number>) or with a word.

    Input:

    <title>{{title}}</title>
    <link>{{link}}</link>

    Output:

    <a href="{{link}}">{{title}}</a>

    If you want to insert data in multiple slots simultaneously in the output, you can do so simply
    by providing a space-separated list of the numbers/labels of the data in one slot. This is useful
    for HTML with a lot of pointless inline elements.

    Input:

    <div><span class="author">{{author}}</span> <span class="title">{{title}}</span> <span class="year">{{year}}</span></div>

    Output:

    <div>{{author title year}}</div>

    If you only want to use numbers, you may specify ranges as well:

    Input:

    <div><span class="author">{{1}}</span> <span class="title">{{2}}</span> <span class="year">{{3}}</span></div>

    Output:

    <div>{{1..3}}</div>

    Note that ranges are inclusive of both upper and lower limits.

    A slot with a colon in it, {{:}}, is a null slot. It means there is some information there that
    isn't interesting, and so reify should skip over it. If you are working with markup that contains,
    for example, randomly-generated strings, you can put a null slot where that string would be and
    reify will be able to handle it. When numbering slots, null slots are not counted.

    Input:

    <div class="article" uuid="{{:}}">{{1}}</div>

    Output:

    <article>{{1}}</article>
    """
    pass


@reify.command("subs")
@click.option("-it", "--input-template", required=True, prompt="Input template",
              help="Path to the template pattern you want to replace")
@click.option("-ot", "--output-template", required=True, prompt="Output template",
              help="Path to the template pattern to replace the old pattern with")
@click.option("-f", "--file", required=True, prompt="File you want to search in",
              help="Path to the file to perform find-and-replace on")
@click.option("-I", "--in-place", is_flag=True,
              help="If set, the substitution will be performed directly on the file")
@click.option("-W", "--compress-whitespace", is_flag=True,
              help="If set, newlines and other series of whitespace will be ignored")
def subs(input_template, output_template, file, in_place, compress_whitespace):
    """Find a pattern in a document and replace it with different formatting"""
    p = TemplateProcessor(input_template, output_template, compress_whitespace)
    click.echo(p.find_and_replace(file, in_place))


@reify.command("generate")
@click.option("-it", "--input-template", required=True, prompt="Input template",
              help="Path to an input template")
@click.option("-ot", "--output-template", required=True, prompt="Output template",
              help="Path to the template you you're replacing it with")
@click.option("-W", "--compress-whitespace", is_flag=True,
              help="If set, newlines and other series of whitespace will be ignored")
def generate(input_template, output_template, compress_whitespace):
    """Generate regular expression patterns to use in your own find-and-replace tool"""
    p = TemplateProcessor(input_template, output_template, compress_whitespace)
    with open("%s.regex" % input_template, "w") as input_regex, \
            open("%s.regex" % output_template, "w") as output_regex:
        input_regex.write(p.pattern)
        output_regex.write(p.target)

    click.echo("Compiled regular expressions written to %s.regex and %s.regex" % (input_template, output_template))


@reify.command("find")
@click.option("-t", "--template", required=True, prompt="Input template",
              help="Path to the template you want to search against")
@click.option("-f", "--file", required=True, prompt="File to search in",
              help="Path to the file you want to search in")
@click.option("-W", "--compress-whitespace", is_flag=True,
              help="If set, newlines and other series of whitespace will be ignored")
def find(template, file, compress_whitespace):
    """Find a pattern in a file"""
    p = TemplateProcessor(template, None, compress_whitespace)
    matches = tuple(p.find(file))
    num_matches = len(matches)

    click.echo("Found %d occurrences matching template %s in %s" % (num_matches, template, file))
    click.echo("(Slot data is highlighted in green)")
    for i, m in enumerate(matches):
        click.echo()
        click.secho("Match %d" % (i + 1), fg="red")
        first_group = m.start(1)
        click.echo(m.group(0)[0:first_group - m.start(0)], nl=False)
        click.secho(m.group(0)[first_group - m.start(0):m.end(1) - m.start(0)],
                    bold=True, bg="green", nl=False)
        for j in range(2, len(m.groups()) + 1):
            end_of_prev_group = m.end(j - 1) - m.start(0)
            start_of_next_group = m.start(j) - m.start(0)
            end_of_next_group = m.end(j) - m.start(0)

            click.echo(m.group(0)[end_of_prev_group:start_of_next_group], nl=False)
            click.secho(m.group(0)[start_of_next_group:end_of_next_group],
                       bold=True, bg="green", nl=False)

        click.echo(m.group(0)[m.end(len(m.groups())) - m.start(0):m.end(0) - m.start(0)])
