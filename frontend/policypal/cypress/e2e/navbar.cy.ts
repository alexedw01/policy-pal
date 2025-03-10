describe('Navbar Component', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/');
  });

  it('should navigate to home page', () => {
    cy.contains('Policy Pal').click();
    cy.url().should('eq', 'http://localhost:3000/');
  });

  it('should navigate to advanced search page', () => {
    cy.contains('Advanced Search').click();
    cy.url().should('include', '/search-adv');
  });

  it('should navigate to trending page', () => {
    cy.contains('Trending').click();
    cy.url().should('include', '/trending');
  });

  it('should navigate to about page', () => {
    cy.contains('About').click();
    cy.url().should('include', '/about');
  });

  it('should navigate to external links', () => {
    cy.contains('Register to Vote!').should('have.attr', 'href').and('include', 'vote.gov');
    cy.contains('Contact Representatives!').should('have.attr', 'href').and('include', 'usa.gov/elected-officials');
  });

});