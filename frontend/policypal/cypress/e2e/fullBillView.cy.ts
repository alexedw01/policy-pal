describe('Full Bill View Component', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/bills/1');
  });

  it('should display full bill information', () => {
    cy.contains('Bill Information').should('be.visible');
    cy.contains('Sponsor').should('be.visible');
    cy.contains('Latest Action').should('be.visible');
  });

  it('should display AI summary if available', () => {
    cy.contains('AI Summary').should('be.visible');
  });

  it('should display full bill text if available', () => {
    cy.contains('Full Bill Text').should('be.visible');
  });

  it('should navigate to Congress.gov on click', () => {
    cy.contains('View on Congress.gov').should('have.attr', 'href').and('include', 'congress.gov');
  });
});