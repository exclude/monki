import crypt
import mistune
import re

from monki.boards.models import Post


class BlockGrammar(mistune.BlockGrammar):
    pass


class BlockLexer(mistune.BlockLexer):
    grammar_class = BlockGrammar

    default_rules = [
        'newline', 'hrule', 'block_code', 'fences', 'heading', 'nptable',
        'lheading', 'list_block', 'block_html', 'def_links', 'def_footnotes',
        'table', 'paragraph', 'text'
    ]


class InlineGrammar(mistune.InlineGrammar):
    quote = re.compile(r'^>(.*)')

    ref = re.compile(r'>>(\d+)')

    spoiler = re.compile(r'^==(?=\S)([\s\S]+?\S)==')


class InlineLexer(mistune.InlineLexer):
    grammar_class = InlineGrammar

    default_rules = [
        'escape', 'inline_html', 'autolink', 'url', 'footnote', 'link',
        'reflink', 'nolink', 'double_emphasis', 'emphasis', 'code',
        'linebreak', 'spoiler', 'strikethrough', 'ref', 'quote', 'text'
    ]

    inline_html_rules = [
        'escape', 'autolink', 'url', 'link', 'reflink', 'nolink',
        'double_emphasis', 'emphasis', 'code', 'linebreak', 'spoiler',
        'strikethrough', 'text',
    ]

    def output_quote(self, match):
        return self.renderer.quote(match.group(0))

    def output_ref(self, match):
        return self.renderer.ref(match)

    def output_spoiler(self, m):
        text = self.output(m.group(1))
        return self.renderer.spoiler(text)


class Renderer(mistune.Renderer):

    def quote(self, match):
        return '<span class="greentext">%s</span>' % mistune.escape(match)

    def ref(self, match):
        try:
            post = Post.objects.get(pk=match.group(1))
        except Post.DoesNotExist:
            return '<span class="broken-quote">{}</span>'.format(
                mistune.escape(match.group(0))
            )

        return '<a href="{}" class="ref" data-post-id="{}">{}</a>'.format(
            post.get_absolute_url(),
            match.group(1),
            mistune.escape(match.group(0))
        )

    def spoiler(self, match):
        return '<span class="spoiler">%s</span>' % mistune.escape(match)

    def image(self, src, title, text):
        return self.link(src, title, text)

    def link(self, link, title, text):
        if not text:
            text = link

        return super().link(link, title, text)


class Markdown(mistune.Markdown):
    pass


def markdown(text, **options):
    renderer = Renderer(escape=True, hard_wrap=True)
    inline = InlineLexer(renderer)
    block = BlockLexer(BlockGrammar())

    return Markdown(renderer=renderer, block=block, inline=inline)(text)


def tripcode(trip):
    """
    Calculates tripcode.

    >>> tripcode('abc')
    'GmgU93SCyE'
    >>> tripcode('abç') # (ab?)
    'zirdg0PztY'
    >>> tripcode('ab')
    '85qvGhCCNc'
    >>> tripcode('a')
    'ZnBI2EKkq.'
    >>> tripcode('ﾌﾌﾌﾌﾌ')
    '6GYLD.0/zY'
    >>> tripcode('ｶｶｶｶｶ')
    'j8YimsZ8Kc'
    >>> tripcode('文')
    'OGxz0qq1Z6'
    """

    # Convert to Shift JIS.
    trip = bytes(trip, 'sjis', 'xmlcharrefreplace').decode('utf-8', 'ignore')


    # Input mangling step is poorly defined and typically a side-effect of
    # mishandling strings long before they end up here. So let's not do it.

    # Derive salt.

    salt = (trip + 'H..')[1:3].translate('................................'
                                         '.............../0123456789ABCDEF'
                                         'GABCDEFGHIJKLMNOPQRSTUVWXYZabcde'
                                         'fabcdefghijklmnopqrstuvwxyz.....'
                                         '................................'
                                         '................................'
                                         '................................'
                                         '................................')

    return crypt.crypt(trip, salt)[3:]


def name_and_tripcode(name):
    """
    >>> name_and_tripcode('')
    (None, None)
    >>> name_and_tripcode(None)
    (None, None)
    >>> name_and_tripcode('#tripcode')
    (None, '3GqYIJ3Obs')
    >>> name_and_tripcode('user#tripcode')
    ('user', '3GqYIJ3Obs')
    >>> name_and_tripcode('##tripcode')
    (None, 'eXwgjmQ.76')
    >>> name_and_tripcode('user##tripcode')
    ('user', 'eXwgjmQ.76')
    """

    try:
        name, *trips = name.split('#')
    except AttributeError:
        return None, None
    else:
        trip = '#'.join(trips)

    if not name:
        name = None

    if not trip:
        trip = None
    else:
        trip = tripcode(trip)

    return name, trip


if __name__ == "__main__":
    import doctest
    doctest.testmod()
