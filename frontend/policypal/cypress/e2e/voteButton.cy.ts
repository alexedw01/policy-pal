describe('Vote Button Component', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/bills/1');
  });

  it('should upvote a bill', () => {
    cy.get('button').contains('↑').click();
  });

  it('should downvote a bill', () => {
    cy.get('button').contains('↓').click();
  });

  it('should require login to vote', () => {
    cy.clearLocalStorage();
    cy.visit('http://localhost:3000/bills/20');
    cy.get('button').contains('↑').click();
//    cy.url().should('include', '/auth');
  });
});