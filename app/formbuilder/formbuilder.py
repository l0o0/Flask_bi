#!/usr/bin/env python

import re
import json

class formLoader:
    
    def __init__(self, form_json, form_action):
        #print form_json
        self.form_data = form_json
        self.action = form_action

    def render_form(self):
        """
        Render Form
        """
        if (not self.form_data or not self.action):
            return False

        fields = '' 

        for field in self.form_data['fields']:

            if field['type'] == 'element-single-line-text':
                fields += self.element_single_line_text(field)

            if field['type'] == 'element-number':
                fields += self.element_number(field)

            if field['type'] == 'element-paragraph-text':
                fields += self.element_paragraph_text(field)

            if field['type'] == 'element-checkboxes':
                fields += self.element_checkboxes(field)

            if field['type'] == 'element-multiple-choice':
                fields += self.element_multiple_choice(field)

            if field['type'] == 'element-dropdown':
                fields += self.element_dropdown(field)

            if field['type'] == 'element-section-break':
                fields += self.element_section_break(field)

        form = self.open_form(fields)

        return form

    def open_form(self, fields):
        """
        Render the form header
        """
        html = '''<form action="{0}" method="post" accept-charset="utf-8" role="form" novalidate="novalidate" >'''.format(self.action);
        html += '''<div class="form-title">'''
        html += u'''<h2>{0}</h2><h3>{1}</h3>'''.format(self.form_data['title'], self.form_data['description'])
        html += fields
        html += '''<button type="submit" class="btn btn-primary">Submit</button>'''
        html += '''</div></form>'''

        return html

    def encode_element_title(self, title):
        """
        Encode Element Title
        """
        return title

    def make_label(self, id, title, required):
        """
        Get formatted label for form element
        """
        if required:
            html = u'''<label for="{0}">{1} <span style="color: red">*</span></label>'''.format(id, title)
        else:
            html = u'''<label for="{0}">{1} </label>'''.format(id, title)

        return html

    def element_single_line_text(self, field):
        """
        Render single line text
        """
        id = self.encode_element_title(field['title'])
        required = 'required' if field['required'] else False

        html = '''<div class="form-group">'''
        html += self.make_label(id, field['title'], required)
        html += u'''<input type="text" name="{0}" id="{0}" class="form-control {1}">'''.format(id, required)
        html += '''</div>'''

        return html

    def element_number(self, field):
        """
        Render number
        """
        id = self.encode_element_title(field['title'])
        required = 'required' if field['required'] else False

        html = '''<div class="form-group">'''
        html += self.make_label(id, field['title'], required)
        html += u'''<input type="number" name="{0}" id="{0}" class="form-control {1}">'''.format(id, required)
        html += '''</div>'''

        return html

    def element_paragraph_text(self, field):
        """
        Render paragraph text
        """
        id = self.encode_element_title(field['title'])
        required = 'required' if field['required'] else False

        html = '''<div class="form-group">'''
        html += self.make_label(id, field['title'], required)
        html += u'''<textarea id="{0}" name="{0}" class="form-control {1}" rows="1"></textarea>'''.format(id, required)
        html += '''</div>'''

        return html

    def element_multiple_choice(self, field):
        """
        Render checkboxes
        """
        id = self.encode_element_title(field['title'])
        required = 'required' if field['required'] else False

        html = '''<div class="form-group">'''
        html += self.make_label(id, field['title'], required)

        for i in xrange(len(field['choices'])):
            #checked = 'checked' if field['choices'][i]['checked'] else ''
            checked=""

            html += '''<div class="checkbox"><label>'''
            html += u'''<input type="checkbox" name="{0}_{1}" id="{0}-{1}" value="{2}" {3}>{4}'''.format(id, i, field['choices'][i]['value'], checked, field['choices'][i]['title'])

            if field['choices'][i]['value'] == 'Others':
                html += u'''<input type="text" name="other_reason" />'''

            html += '''</label></div>'''

        html += '''</div>'''

        return html

    def element_checkboxes(self, field):
        """
        Render multiple choice
        """
        id = self.encode_element_title(field['title'])
        required = 'required' if field['required'] else False

        html = '''<div class="form-group">'''
        html += self.make_label(id, field['title'], required)

        for i in xrange(len(field['choices'])):
            checked = ''

            html += '''<div class="radio"><label>'''
            html += u'''<input type="radio" name="{0}" id="{0}_{1}" value="{2}" {3}>{4}'''.format(id, i, field['choices'][i]['value'], checked, field['choices'][i]['title'])
            
            if field['choices'][i]['value'] == 'Others':
                html += u'''<input type="text" name="other_reason" />'''    

            html += '''</label></div>'''

        html += '''</div>'''

        return html

    def element_dropdown(self, field):
        """
        Render dropdown
        """
        id = self.encode_element_title(field['title'])
        required = 'required' if field['required'] else False

        html = '''<div class="form-group">'''
        html += self.make_label(id, field['title'], required)
        html += u'''<select name="{0}" id="{0}" class="form-control {1}">'''.format(id, required)

        for choice in field['choices']:
            checked = 'selected' if choice['checked'] else ''
            html += u'''<option value="{0}" {1}>{2}</option>'''.format(choice['value'], checked, choice['title'])

        html += '</select></div>'

        return html

    def element_section_break(self, field):
        html = '''<div class="form-group section-break">'''
        html += u'''<hr/><h4>{0}</h4><p>{1}</p>'''.format(field['title'], field['description'])
        html += '''</div>'''

        return html
