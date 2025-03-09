describe('SearchBar Component', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/');
  });

  it('should perform a search and navigate to results page', () => {
    cy.get('input[placeholder="Search bills..."]').type('Healthcare');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/search?keyword=Healthcare');
    cy.contains('Search Results for "Healthcare"').should('be.visible');
  });

  it('should not navigate if search input is empty', () => {
    cy.get('button[type="submit"]').click();
    cy.url().should('eq', 'http://localhost:3000/');
  });
});