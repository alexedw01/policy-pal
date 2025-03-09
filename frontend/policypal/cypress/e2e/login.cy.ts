describe('Login Component', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/auth');
  });

  it('should display login form', () => {
    cy.contains('Sign in to your account').should('be.visible');
    cy.get('input[name="email"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('button[type="submit"]').contains('Sign in').should('be.visible');
  });

  it('should login successfully with valid credentials', () => {
    cy.intercept('POST', '/api/auth/login', { statusCode: 200, body: { access_token: 'fake-jwt-token', user: { email: 'test@example.com' } } }).as('loginRequest');
    cy.get('input[name="email"]').type('testuser@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').contains('Sign in').click();
    cy.wait('@loginRequest');
    cy.url().should('eq', 'http://localhost:3000/');
    cy.contains('Logout').should('be.visible');
  });

  it('should show error message with invalid credentials', () => {
    cy.intercept('POST', '/api/auth/login', { statusCode: 401, body: { error: 'Invalid credentials' } }).as('loginRequest');
    cy.get('input[name="email"]').type('testuser@example.com');
    cy.get('input[name="password"]').type('wrongpassword');
    cy.get('button[type="submit"]').contains('Sign in').click();
    cy.wait('@loginRequest');
    cy.contains('Invalid credentials').should('be.visible');
  });
});