Project{
	name: "gap_client"
	
	Product {
		Group{
			name: "Code"
			prefix: "gap_client"
			excludeFiles: "/**/internal/**/*"
			files: [
				"/**/*.py",
			]
		}
		Group{
			name: "Test"
			prefix: "tests"
			excludeFiles: "/**/internal/**/*"
			files: [
				"/**/*.py",
				"/**/Makefile",
				"/**/*.ini",
			]
		}
		Group{
			name: "Examples"
			prefix: "examples"
			excludeFiles: "/**/internal/**/*"
			files: [
				"/**/*.py",
			]
		}
		Group{
			name: "Meta"
			prefix: "./"
			excludeFiles: "/**/internal/**/*"
			files: [
				"*.conf",
				"*.py",
				"*.qbs",
				".gitignore",
				".env",
				"Makefile",
				"README.md",
				"VERSION",
				"LICENCE",
				"CHANGELOG",
				"config.yaml",
				"azure-pipelines.yml",
				"requirements/*",
				"setup.*",
				".github/**/*",
			]
		}
	}
}
