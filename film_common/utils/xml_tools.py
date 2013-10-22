def xml_to_dict(el, force_list=(), strip=True):
    out = {}
    out.update(el.items())
    if(el.text and el.text.strip()):
        out['text'] = el.text.strip() if strip else el.text
    for sub in el:
        if len(sub) or sub.items():
            content = xml_to_dict(sub, force_list)
        else:
            content = sub.text or ''
            if strip:
                content = content.strip()
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

