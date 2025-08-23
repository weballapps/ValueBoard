# Claude Code GitHub Integration Setup

This guide will help you set up Claude Code workflows and automated code review in your GitHub repository.

## 🚀 Quick Start

### 1. Repository Secrets Setup

First, add these secrets to your GitHub repository:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add these repository secrets:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
RENDER_DEPLOY_HOOK_URL=your_render_deployment_webhook_url
```

### 2. Enable GitHub Actions

1. Go to your repository → Actions
2. If Actions are disabled, click "I understand my workflows, go ahead and enable them"
3. The workflows will be automatically available once you push the `.github` directory

## 🔧 Available Workflows

### 1. Claude Code Review (`claude-code-review.yml`)

**Triggers:**
- Automatically on every Pull Request
- On pushes to `main` and `develop` branches

**Features:**
- Automated code review using Claude
- Python linting and formatting checks
- Security scanning with Bandit
- Dependency vulnerability checking
- Custom focus on financial calculations and data validation

### 2. Claude Code Workflow (`claude-code-workflow.yml`)

**Triggers:**
- Manual trigger with custom task description
- Can be triggered from Issues with specific labels

**Features:**
- Execute custom coding tasks via Claude
- Automatic Pull Request creation
- Code validation and testing
- Supports different focus areas (performance, security, refactoring, etc.)

### 3. Deploy to Render (`deploy-render.yml`)

**Triggers:**
- Automatic on pushes to `main`
- On merged Pull Requests
- Manual trigger

**Features:**
- Automated deployment to Render
- Build info generation
- Syntax and import validation

## 📋 How to Use

### Using Claude Code Review

1. **Automatic Review**: Simply create a Pull Request - Claude will automatically review it
2. **Focus Areas**: Claude will focus on:
   - Financial calculation accuracy
   - Security vulnerabilities
   - Performance optimization
   - Code maintainability
   - Python best practices

### Using Claude Code Workflow

#### Method 1: Manual Workflow Dispatch

1. Go to Actions → Claude Code Workflow
2. Click "Run workflow"
3. Fill in the task description
4. Select focus area
5. Optionally specify target files
6. Click "Run workflow"

#### Method 2: Issue-based Tasks

1. Create a new issue using the "Claude Code Task" template
2. Fill in the task details
3. Add the `claude-code` label
4. Claude will automatically process the task and create a PR

### Example Tasks

```yaml
# Performance optimization
Task: "Optimize the stock screening function to handle larger datasets more efficiently"
Focus: performance

# Security improvement  
Task: "Add input validation and sanitization for all user inputs in the stock analysis"
Focus: security

# Feature development
Task: "Add support for cryptocurrency analysis alongside stock analysis"
Focus: feature-development

# Bug fixing
Task: "Fix the debt-to-equity ratio calculation displaying incorrect values"
Focus: bug-fixing
```

## 🛠 Configuration

### Claude Code Config (`.github/claude-code-config.yml`)

This file controls Claude's behavior:

```yaml
review:
  focus_areas:
    - security
    - performance  
    - financial_accuracy
  
  custom_instructions: |
    Focus on financial calculation accuracy and API error handling
```

### Issue Templates

Three templates are provided:
- **Claude Code Task**: Request automated coding tasks
- **Bug Report**: Report issues with focus on financial calculations
- **Feature Request**: Suggest new features with market scope

### Pull Request Template

Comprehensive template with:
- Change type classification
- Financial accuracy verification checklist
- Performance impact assessment
- Security considerations

## 🔒 Security Setup

### API Keys

1. **Anthropic API Key**: Get from https://console.anthropic.com
   - Add as `ANTHROPIC_API_KEY` secret
   - Required for Claude Code functionality

2. **Render Deploy Hook**: Get from your Render service settings
   - Add as `RENDER_DEPLOY_HOOK_URL` secret
   - Required for automatic deployments

### Permissions

The workflows require these permissions:
- `contents: write` - To create branches and commits
- `pull-requests: write` - To create and comment on PRs
- `issues: write` - To comment on issues

## 📊 Monitoring and Artifacts

### Workflow Artifacts

Each workflow generates artifacts:
- **Code Analysis Reports**: Linting, security scan results  
- **Claude Task Outputs**: Detailed task execution logs
- **Deployment Logs**: Build and deployment information

### Notifications

Configure notifications for:
- Successful deployments
- Failed code reviews
- Security alerts
- Task completions

## 🎯 Best Practices

### For Claude Tasks

1. **Be Specific**: Provide detailed task descriptions
2. **Set Context**: Include relevant background information
3. **Define Success**: Use clear acceptance criteria
4. **Review Results**: Always review Claude's changes before merging

### For Code Reviews

1. **Focus Areas**: Claude reviews focus on financial accuracy and security
2. **Manual Review**: Still perform manual reviews for business logic
3. **Test Changes**: Always test financial calculations manually
4. **Documentation**: Update documentation for significant changes

### For Deployments

1. **Test First**: Always test in development before merging to main
2. **Monitor**: Watch deployment logs for issues
3. **Rollback Plan**: Know how to rollback if needed
4. **Staging**: Consider using a staging environment

## 🐛 Troubleshooting

### Common Issues

1. **Workflow not triggering**:
   - Check if GitHub Actions are enabled
   - Verify the workflow file syntax
   - Check repository permissions

2. **Claude Code failing**:
   - Verify `ANTHROPIC_API_KEY` is set correctly
   - Check API quota and limits
   - Review workflow logs for specific errors

3. **Deployment issues**:
   - Verify `RENDER_DEPLOY_HOOK_URL` is correct
   - Check Render service status
   - Review deployment logs

### Getting Help

1. Check workflow run logs in the Actions tab
2. Review the artifacts for detailed error information
3. Create an issue using the provided templates
4. Check Claude Code documentation

## 🔄 Workflow Examples

### Example 1: Performance Optimization Task

```markdown
## Task Description
Optimize the stock screening function to handle 1000+ stocks efficiently

## Focus Area  
- [x] Performance optimization

## Specific Requirements
- Reduce screening time from 3+ minutes to under 1 minute
- Implement proper caching mechanisms
- Add progress indicators for user feedback

## Target Files
- stock_value_dashboard.py (screening functions)

## Acceptance Criteria
- [ ] Screening completes in under 60 seconds for 500 stocks
- [ ] Memory usage remains stable during large screens  
- [ ] User sees progress feedback during screening
```

### Example 2: Security Enhancement Task

```markdown
## Task Description
Add comprehensive input validation and sanitization for all user inputs

## Focus Area
- [x] Security improvements

## Specific Requirements  
- Validate stock symbols against known formats
- Sanitize all user text inputs
- Add rate limiting for API calls
- Implement proper error handling without information leakage

## Acceptance Criteria
- [ ] All user inputs are validated and sanitized
- [ ] No sensitive information exposed in error messages
- [ ] Rate limiting prevents API abuse
- [ ] Security scan passes without high-risk findings
```

---

## 📞 Support

For issues with this setup:
1. Check the troubleshooting section above
2. Review GitHub Actions documentation
3. Create an issue in this repository
4. Contact Claude Code support

**Happy coding with Claude! 🤖✨**