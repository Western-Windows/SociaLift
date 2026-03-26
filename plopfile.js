export default function (plop) {
    // We are creating a generator called "feature"
    plop.setGenerator('feature', {
        description: 'Create a new feature folder with its dependencies',

        // 1. Ask the user for the name of the feature
        prompts: [
            {
                type: 'input',
                name: 'name',
                message: 'What is the name of your feature/component?',
            },
        ],

        // 2. What actions to take with that name
        actions: [
            // Action A: Create the main TypeScript/Component file
            {
                type: 'add',
                path: 'src/features/{{pascalCase name}}/{{pascalCase name}}.tsx', // Use .vue or .ts if not using React
                templateFile: 'plop-templates/Component.tsx.hbs',
            },
            // Action B: Create the CSS/Styles file
            {
                type: 'add',
                path: 'src/features/{{pascalCase name}}/{{pascalCase name}}.css',
                templateFile: 'plop-templates/Component.css.hbs',
            },
            // Action C: Create an index file for easy importing
            {
                type: 'add',
                path: 'src/features/{{pascalCase name}}/index.ts',
                templateFile: 'plop-templates/index.ts.hbs',
            }
        ],
    });
}