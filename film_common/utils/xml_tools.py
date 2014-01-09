import HTMLParser
_parser = HTMLParser.HTMLParser()

def xml_to_dict(el, force_list=(), strip=True, unescape=False):
    def _conv(s):
        if strip:
            s = s.strip()
        if unescape:
            s = _parser.unescape(s)
        return s

    out = {}
    out.update(el.items())
    if(el.text and el.text.strip()):
        out['text'] = _conv(el.text)
    for sub in el:
        if len(sub) or sub.items():
            content = xml_to_dict(sub, force_list, strip=strip, unescape=unescape)
        else:
            content = _conv(sub.text or '')
        if sub.tag in out:
            item = out[sub.tag]
            if isinstance(item, list):
                item.append(content)
            else:
                out[sub.tag] = [item, content]
        else:
            if sub.tag in force_list:
                content = [content]
            out[sub.tag] = content
    return out

