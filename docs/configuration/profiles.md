Built-in Profile for isort
========

The following profiles are built into isort to allow easy interoperability with
common projects and code styles.

To use any of the listed profiles, use `isort --profile PROFILE_NAME` from the command line, or `profile=PROFILE_NAME` in your configuration file.


#black


 - **multi_line_output**: `3`
 - **include_trailing_comma**: `True`
 - **force_grid_wrap**: `0`
 - **use_parentheses**: `True`
 - **ensure_newline_before_comments**: `True`
 - **line_length**: `88`

#django


 - **combine_as_imports**: `True`
 - **include_trailing_comma**: `True`
 - **multi_line_output**: `5`
 - **line_length**: `79`

#pycharm


 - **multi_line_output**: `3`
 - **force_grid_wrap**: `2`
 - **lines_after_imports**: `2`

#google


 - **force_single_line**: `True`
 - **force_sort_within_sections**: `True`
 - **lexicographical**: `True`
 - **single_line_exclusions**: `('typing',)`
 - **order_by_type**: `False`
 - **group_by_package**: `True`

#open_stack


 - **force_single_line**: `True`
 - **force_sort_within_sections**: `True`
 - **lexicographical**: `True`

#plone


 - **force_alphabetical_sort**: `True`
 - **force_single_line**: `True`
 - **lines_after_imports**: `2`
 - **line_length**: `200`

#attrs


 - **atomic**: `True`
 - **force_grid_wrap**: `0`
 - **include_trailing_comma**: `True`
 - **lines_after_imports**: `2`
 - **lines_between_types**: `1`
 - **multi_line_output**: `3`
 - **use_parentheses**: `True`

#hug


 - **multi_line_output**: `3`
 - **include_trailing_comma**: `True`
 - **force_grid_wrap**: `0`
 - **use_parentheses**: `True`
 - **line_length**: `100`

#wemake


 - **multi_line_output**: `3`
 - **include_trailing_comma**: `True`
 - **use_parentheses**: `True`
 - **line_length**: `80`
