# ssg-vale-rules-gen
Python script to generate Vale linting rules from word usage guidance in the Red Hat Supplementary Style Guide. These rules are used in the [Vale at Red Hat project](https://github.com/redhat-documentation/vale-at-red-hat).

## Building output
1. Run the python build locally, and commit all changes.
2. Create a new tag, for example, `git tag v2`.	
3. Push the tag, `git push origin --tags`

The SupplementaryStyleGuide .yml rules are published in the releases section of the github repo. 
