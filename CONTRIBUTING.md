# Git Collaboration Guidelines

## GP0) Branch Naming Convention  
- Every branch must be created from an **issue** and follow this pattern:  
  ```
  issuenumber-description-of-branch
  ```
- Example branch names:
  - `6-added-git-collaboration-guidelines`
  - `11-fixed-error-editing-memory-trace`

## GP1) Atomic Commits  
- Each commit must contain **only one atomic change**, meaning it did **one thing only** that could be **summarized in a single sentence**.

## GP2) Commit Message Format  
- Each commit message must have:
  - **Be clear and descriptive**
  - **Be traceable** (linked to a pull request and an issue)
  - **Include a prefix** to indicate the type of change:
    ```
    Fixed bug in airport data filtering
    Created a new visualization for flight data
    Refactored database connection handling
    ```

## GP3) Issue-Based Workflow  
- Work should be **split into issues** and **assigned to team members**.

## GP4) Issue Closure  
- Every issue should be **closed through a pull request**.

## GP5) Main Branch Protection  
- **Commits must never be made directly to the `main` branch**.  
- All changes must go through **pull requests**.

## GP6) Pull Request Review  
- **A pull request must be reviewed and merged by a different team member** than the one who submitted it.
