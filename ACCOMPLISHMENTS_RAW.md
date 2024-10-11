* PR #115 - [Enhancement] Authentication Checking with Bearer Token
   * Commit: chore: resolved conflict with dev

* PR #104 - [Refactor] Enhance DAL with Improved Error Handling and Pagination
   * Commit: refactor(dataAccess): streamline handlers and remove unused code
      - Simplify ApplicationHandler, AuthorityHandler, and RoleHandler constructors
      - Remove RoleApplicationHandler and RoleAuthorityHandler
      - Delete unused RoleApplicationRepository and RoleAuthorityRepository
      - Update UserRepository and UserService with getUserApplications method
      - Refactor API routes to use new handler methods and error handling
      - Remove unused role-applications and role-authorities API routes
      - Update imports to use @dal alias consistently
   * Commit: chore: resolved conflict with dev
   * Commit: chore: updated return payload
   * Commit: chore: removed jest unit test
   * Commit: refactor(api): streamline API constants and update dependencies
      - Remove bosa-client-container-sdk dependency
      - Update next-intl to version 3.20.0
      - Refactor API constants for applications, authorities, and roles
      - Remove unused roleApplications and roleAuthorities constants
      - Update API endpoints for role and application relationships
      - Adjust imports and usage in affected components
      - Update UserHandler to use new API constants
   * Commit: refactor(api): standardize API endpoint naming conventions
      - Rename API constants for consistency:
      * Change 'BY' to 'FROM' in API endpoint names
      * Update 'CREATE' to 'ADD' for relationship endpoints
      * Update 'DELETE' to 'REMOVE' for relationship endpoints
      - Update imports and usages in affected components
      - Add file header to src/services/dashboard/common.tsx
      - Update API endpoint usage in getDashboardAuthorities function
   * Commit: chore: resolved conflict with dev
   * Commit: fix(api): correct data extraction from API responses
      - Update API calls to properly extract data from response.json().data
      - Fix type mismatch in getDashboardAuthorities for role ID
      - Ensure consistent data handling across components (applications, roles, users)
      - Update imports to use correct API constants
      - Remove outdated TODO comments and unused imports
   * Commit: chore: resolved conflict with dev
   * Commit: fix: fixed endpoints
   * Commit: feat: added api.json for postman
   * Commit: chore: updated types to use global types
