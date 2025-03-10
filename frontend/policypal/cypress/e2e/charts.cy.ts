describe('Charts Component', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/bills/20');
  });

  it('should display loading message initially', () => {
    cy.contains('Loading demographics...').should('be.visible');
  });

  /*
  it('should display error message if there is an error', () => {
    cy.intercept('GET', '/api/bills/1/demographics', { statusCode: 500 }).as('getDemographics');
    cy.visit('http://localhost:3000/bills/20');
    cy.wait('@getDemographics');
    cy.contains('Error:').should('be.visible');
  }); */

  it('should display bar chart and pie chart', () => {
    cy.intercept('GET', '/api/bills/20/demographics', { fixture: 'demographics.json' }).as('getDemographics');
    cy.visit('http://localhost:3000/bills/20');
    cy.wait('@getDemographics');
    cy.contains('Political Affiliation - Vote Percentages').should('be.visible');
    cy.contains('Political Affiliation - Total Votes').should('be.visible');
    cy.get('.recharts-bar').should('have.length.greaterThan', 0);
    cy.get('.recharts-pie').should('have.length.greaterThan', 0);
  });

  it('should change charts when selecting different demographic category', () => {
    cy.intercept('GET', '/api/bills/20/demographics', { fixture: 'demographics.json' }).as('getDemographics');
    cy.visit('http://localhost:3000/bills/20');
    cy.wait('@getDemographics');
    cy.get('#category-select').select('Age Brackets');
    cy.contains('Age Brackets - Vote Percentages').should('be.visible');
    cy.contains('Age Brackets - Total Votes').should('be.visible');
  });
});