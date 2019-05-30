import click
from TemplateProcessor import *


@click.group("reify")
def reify():
    """The Reify Template Compiler v. 0.1

    Reify is a simple templating language that compiles to regular expression syntax to make finding
    and replacing complex patterns with other complex patterns less of a pain.

    The intended use-case of Reify is to find and replace large amounts of repetitive (usually
    computer-generated) XML and HTML markup, while retaining whatever content the user wants.
    However it will work for arbitrary text documents.

    \b
    For a rundown of how the Reify templating language works, consult the
    README for this project on GitHub:
    https://github.com/periodicaidan/reify#templating-language

    \b
    For more detailed instructions on using Reify, you can browse the various
    help menus in the command line using `reify <command> --help` or you can
    read about them on GitHub:
    https://github.com/periodicaidan/reify#command-line-interface
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


@reify.command("license")
def license_():
    """View license information"""
    with open("LICENSE", "r") as license_file:
        click.echo(license_file.read())
