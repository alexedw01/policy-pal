describe('Register Component', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/auth');
    cy.contains('Need an account? Sign up').click();
  });

  it('should display register form', () => {
    cy.contains('Create a new account').should('be.visible');
    cy.get('input[name="username"]').should('be.visible');
    cy.get('input[name="email"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('input[name="age"]').should('be.visible');
    cy.get('select[name="gender"]').should('be.visible');
    cy.get('select[name="ethnicity"]').should('be.visible');
    cy.get('select[name="state"]').should('be.visible');
    cy.get('select[name="political_affiliation"]').should('be.visible');
    cy.get('button[type="submit"]').contains('Register').should('be.visible');
  });

  it('should register successfully with valid credentials', () => {
    cy.intercept('POST', '/api/auth/register', { statusCode: 201, body: { message: 'Registration successful' } }).as('registerRequest');
    cy.get('input[name="username"]').type('newuser');
    cy.get('input[name="email"]').type('newuser@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('input[name="age"]').type('25');
    cy.get('select[name="gender"]').select('Male');
    cy.get('select[name="ethnicity"]').select('White');
    cy.get('select[name="state"]').select('California');
    cy.get('select[name="political_affiliation"]').select('Moderate');
    cy.get('button[type="submit"]').contains('Register').click();
    cy.wait('@registerRequest');
    cy.url().should('eq', 'http://localhost:3000/');
  });

  it('should show error message if email is already taken', () => {
    cy.intercept('POST', '/api/auth/register', { statusCode: 409, body: { error: 'Email already taken' } }).as('registerRequest');
    cy.get('input[name="username"]').type('existinguser');
    cy.get('input[name="email"]').type('existinguser@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('input[name="age"]').type('25');
    cy.get('select[name="gender"]').select('Male');
    cy.get('select[name="ethnicity"]').select('White');
    cy.get('select[name="state"]').select('California');
    cy.get('select[name="political_affiliation"]').select('Moderate');
    cy.get('button[type="submit"]').contains('Register').click();
    cy.wait('@registerRequest');
    cy.contains('Email already taken').should('be.visible');
  });
});