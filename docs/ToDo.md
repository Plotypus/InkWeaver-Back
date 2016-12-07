# To-Do List

- Protocol
  - [x] Revise protocol
  - [ ] Revise protocol (yes, again)
    - Rename things so contexts are clear, e.g. `get_all_paragraphs_from_section` or `get_all_section_paragraphs` instead of `get_all_paragraphs`
  - [ ] Fully document new protocol
- Data Model
  - [ ] Assess need for updates
- Database
- Handler
  - [ ] Create decorators
    - [ ] Check user login
    - [ ] Check appropriate context
  - [ ] Fix dispatch error handling
    - Currently assumed *all* `KeyError`s are due to invalid dispatches... which is not the case
- Discussion
