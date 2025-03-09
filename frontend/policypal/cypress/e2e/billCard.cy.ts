describe('Bill Card Component', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/');
  });

  it('should display bill information', () => {
    cy.get('.bill-card').first().within(() => {
      cy.get('h2').should('be.visible');
    });
  });

  it('should navigate to bill details page on click', () => {
    cy.get('.bill-card').first().within(() => {
      cy.get('h2').click();
    });
    cy.url().should('include', '/bills/');
    cy.contains('Latest Action').should('be.visible');
  });

  it('should expand and collapse AI summary', () => {
    cy.get('.bill-card').first().within(() => {
      cy.contains('Read more').click();
      cy.contains('Show less').should('be.visible');
      cy.contains('Show less').click();
      cy.contains('Read more').should('be.visible');
    });
  });
});