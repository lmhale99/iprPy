def showSelection(elementID, options):
    """
    Generates HTML associated with a selection menu that shows content only
    for the value listed. Uses the showSelection() javascript function.
    
    Parameters
    ----------
    elementID (str)
        The name for the element where the content is shown/hidden.  The 
        individual sub-element options and the select element will also be
        given ids with this name as a root.
    options (OrderedDict of str)
        The str names and content associated with each option.
    
    Returns
    str
        The HTML content combining the select and content.
    """
    
    # Start select HTML element
    html_select = []
    html_select.append('<select id="%s" onchange="showSelection(\'%s\', %s)">' 
                       % (elementID+'Select',
                          elementID+'Select',
                          [elementID+'%i' %i for i in xrange(len(options))]))
    
    # Start content HTML div element
    html_content = []
    html_content.append('<div id="%s">' % elementID)
    
    # Loop over all options
    for i, name in enumerate(options):
        
        # Add option name to select
        html_select.append('  <option value="%i">%s</option>' % (i, name))
        
        # Add option content to content
        if i == 0: 
            display = 'block'
        else:
            display = 'none'
        html_content.append('  <div id="%s" style="display:%s;">' % (elementID+str(i), display))
        html_content.append(options[name])
        html_content.append('</div>')
    
    # End select and content
    html_select.append('</select>\n')
    html_content.append('</div>\n')
    
    # Return HTML string
    return '\n'.join(html_select) + '\n'.join(html_content)