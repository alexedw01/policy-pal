describe('Advanced Search Page', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/search-adv');
  });

  it('should load the advanced search page', () => {
    cy.contains('ADVANCED SEARCH').should('be.visible');
  });

  it('should perform a search and display results', () => {
    cy.get('input[placeholder="Search for bills..."]').type('Healthcare');
    cy.get('button[type="submit"]').click();
    cy.contains('Search Results for "Healthcare"').should('be.visible');
    cy.get('.bill-card').should('have.length.greaterThan', 0);
  });

  it('should filter results by chamber', () => {
    cy.get('select').eq(0).select('House');
    cy.get('.bill-card').each(($el) => {
      cy.wrap($el).contains('House').should('be.visible');
    });
  });

  it('should sort results by newest first', () => {
    cy.get('select').eq(1).select('Newest First');
    cy.get('.bill-card').first().contains('Newest Bill Title');
  });

  it('should filter results by date range', () => {
    cy.get('input[type="date"]').eq(0).type('2023-01-01');
    cy.get('input[type="date"]').eq(1).type('2023-12-31');
    cy.get('.bill-card').each(($el) => {
      cy.wrap($el).contains('2023').should('be.visible');
    });
  });
});