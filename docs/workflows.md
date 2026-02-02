# Automated Workflows

ShokeDex uses GitHub Actions workflows to automate maintenance, testing, and improvements. This document describes the available workflows and how to use them.

## Available Workflows

### Daily Performance Improvement Workflow

**File**: `.github/workflows/daily-perf-improver.md`  
**Schedule**: Daily  
**Purpose**: Systematically identify and implement performance optimizations

The daily performance improvement workflow operates in three distinct phases to ensure thorough analysis and implementation:

#### Phase 1: Research and Planning

The workflow analyzes the repository to understand the performance landscape:

- Current performance testing practices and tooling
- User-facing performance concerns (load times, responsiveness, throughput)
- System performance bottlenecks (compute, memory, I/O, network)
- Development workflow performance issues (build times, test execution)
- Existing performance documentation and measurement approaches

**Output**: Creates a discussion titled "Daily Perf Improver - Research and Plan" with:
- Identified optimization targets
- Performance engineering gaps
- Proposed improvement strategy

#### Phase 2: Configuration and Guides

The workflow prepares the environment for performance engineering:

- Analyzes existing CI files and build scripts
- Creates `.github/actions/daily-perf-improver/build-steps/action.yml` with validated build steps
- Generates performance engineering guides in `.github/copilot/instructions/`

**Output**: Creates a pull request with:
- Build steps configuration
- 1-5 performance engineering guides covering relevant areas
- Measurement strategies and tooling documentation

#### Phase 3: Implementation

The workflow implements performance improvements:

- Selects optimization goals from the plan
- Implements code changes (algorithm improvements, caching, resource optimization)
- Measures performance impact with before/after comparisons
- Runs tests to ensure functionality is preserved
- Applies code formatting and linting

**Output**: Creates draft pull requests with:
- Performance improvements with measured impact
- Detailed description of approach and trade-offs
- Reproducible testing instructions
- Updated performance guides with lessons learned

### Controlling Workflows

All workflows can be controlled using the `gh aw` (GitHub Agentic Workflows) CLI:

#### Disable a Workflow

```bash
gh aw disable daily-perf-improver --repo scwardbulldog/ShokeDex
```

#### Enable a Workflow

```bash
gh aw enable daily-perf-improver --repo scwardbulldog/ShokeDex
```

#### Run Manually

```bash
# Single run
gh aw run daily-perf-improver --repo scwardbulldog/ShokeDex

# Multiple iterations (useful for progressing through phases)
gh aw run daily-perf-improver --repo scwardbulldog/ShokeDex --repeat 3
```

#### View Logs

```bash
gh aw logs daily-perf-improver --repo scwardbulldog/ShokeDex
```

### Daily Documentation Updater

**File**: `.github/workflows/daily-doc-updater.md`  
**Schedule**: Daily at 6am UTC  
**Purpose**: Keep documentation current with code changes

The documentation updater automatically:

- Scans for merged pull requests from the last 24 hours
- Identifies new features or changes that need documentation
- Updates relevant documentation files
- Creates pull requests with documentation updates

The workflow follows strict documentation standards including:
- CommonMark compliance
- Diátaxis framework (tutorials, how-to guides, reference, explanation)
- Consistent tone and style
- Code examples with proper syntax highlighting

**Output**: Creates pull requests with:
- Updated documentation for new features
- Links to relevant merged PRs
- Summary of changes made

## Workflow Permissions

Workflows use minimal permissions following security best practices:

- **daily-perf-improver**: Read-only access to repository content
- **daily-doc-updater**: Read access to contents, issues, and pull requests

All workflows use safe-outputs to create discussions, comments, and pull requests without requiring write permissions.

## Performance Targets

The daily performance improvement workflow optimizes for the following targets:

**Raspberry Pi 3B+**:
- 30 FPS rendering
- <80% CPU usage
- <150MB RAM usage
- <50ms input latency

**Raspberry Pi 4**:
- 60 FPS rendering
- <60% CPU usage
- <200MB RAM usage
- <30ms input latency

## Monitoring Workflow Activity

### Check Workflow Status

View workflow runs in the GitHub Actions tab:
- Navigate to repository → Actions
- Select workflow from left sidebar
- View run history and status

### Review Workflow Outputs

The workflows create the following artifacts:

1. **Discussions**: Research plans and progress updates
2. **Pull Requests**: Configuration updates and improvements
3. **Comments**: Status updates and results

### Provide Feedback

You can influence workflow behavior by:

- Adding comments to research discussions
- Reviewing and requesting changes on PRs
- Adjusting workflow schedules in workflow files
- Disabling workflows that aren't needed

## Troubleshooting

### Workflow Not Running

Check if the workflow is enabled:

```bash
gh aw logs daily-perf-improver --repo scwardbulldog/ShokeDex
```

Workflows have a `stop-after` date (1 month for performance improver). They will not trigger after this date unless updated.

### Build Steps Failing

If Phase 2 build steps fail:

1. Review `.github/actions/daily-perf-improver/build-steps/action.yml`
2. Check `build-steps.log` in repository root
3. The workflow will create a fix PR automatically
4. Manually update the PR if needed

### Duplicate Work

The workflow checks for existing PRs to avoid duplicate work. If you notice duplicates:

1. Close one of the duplicate PRs
2. Add a comment to the research discussion noting the issue
3. The workflow will detect closed PRs in subsequent runs

## Best Practices

### Working with Performance Improvements

1. **Review the Plan**: Check the research discussion before the workflow runs Phase 3
2. **Provide Context**: Add comments to discussions with domain knowledge
3. **Test Changes**: Review PRs carefully, especially performance claims
4. **Measure Impact**: Verify performance improvements on actual Raspberry Pi hardware

### Working with Documentation Updates

1. **Quick Review**: Documentation PRs are marked for auto-merge but should be reviewed
2. **Add Context**: If documentation misses important details, add comments
3. **Check Links**: Ensure cross-references and links work correctly

## Related Documentation

- [Raspberry Pi Installation Guide](pi_installation_guide.md) - Setup instructions
- [Performance Optimization Guide](pi_optimization_guide.md) - Manual optimization tips
- [Tools README](../tools/README.md) - Performance profiling tools
- [Testing Guide](../TESTING.md) - Testing approach and strategies

## Additional Resources

- GitHub Agentic Workflows Documentation: [GitHub Next](https://githubnext.com/projects/agentic-workflows)
- PokéAPI: [https://pokeapi.co/](https://pokeapi.co/)
- Pygame Documentation: [https://www.pygame.org/docs/](https://www.pygame.org/docs/)
