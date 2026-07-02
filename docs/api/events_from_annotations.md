# EventsFromAnnotations

::: biopap.modules.events_from_annotations.EventsFromAnnotations

## Example settings for config file

Example settings in correct format for the config file.

```yaml
EventsFromAnnotations:
    regex:   r'(?<=(^RS232 Trigger: ))(\d+)'
    
```
The regular expression should match an integer as the first group (code uses `re.search`). For example, this regex:

`r'(?<=(^RS232 Trigger: ))(\d+)'`

matches the number 23 in the string:

`RS232 Trigger: 23('\u0017')`

Alternatively, you can provide a dictionary containing annotation/event pairs, so for instance:

`{
  "RS232 Trigger: 31('\u001f')": 31,
  "RS232 Trigger: 32(' ')": 32,
  "RS232 Trigger: 34('\"')": 34,
  "RS232 Trigger: 35('#')": 35
}
`
To create a JSON-file with a template dictionary, run the `create_template_annotations_dict()` function from the `helpers' module.
This function will read all annotations from the input file and create a dictionary from the, guessing the corresponding event ID's
from the annotations (or add `?` when it doesn't know). Edit the file to fit your use case, read it back into a dictionary, and
run `EventsFromAnnotations` with assigining the dictionary to the `event_id` parameter.
