<?php
class PathValidator
{
	public function __construct($path)
	{
		$parsed_path = $this->ParsePath($path);
		
		if($parsed_path != null)
		{
			$this->path = $parsed_path;
		}
		else
		{
			throw new Exception("Invalid path specified");
		}
	}
	
	public function ValidatePath($root)
	{
		$root_path = $this->ParsePath($root);
		
		if($root_path != null)
		{
			$root_stack = explode("/", $root_path);
			$path_stack = explode("/", $this->path);
			
			for($i = 0; $i < count($root_stack); $i++)
			{
				if($root_stack[$i] != $path_stack[$i])
				{
					return false;
				}
			}
			
			return true;
		}
		else
		{
			throw new Exception("Specified root path is invalid.");
		}
	}
	
	public function RelativeDepth($root)
	{
		$root_length = substr_count($this->ParsePath($root), "/");
		$path_length = substr_count($this->path, "/");
		
		return $path_length - $root_length;
	}
	
	private function RemoveTrailingSlash($path)
	{
		if(substr($path, strlen($path) - 1) == "/")
		{
			return substr($path, 0, strlen($path) - 1);
		}
		else
		{
			return $path;
		}
	}
	
	private function ParsePath($path)
	{
		/* We use a custom function for this since we just want to resolve the path no matter what,
		 * and the realpath() function will return false if the path either doesn't exist or is not
		 * accessible. */
		 
		$path = $this->RemoveTrailingSlash($path);
		 
		if(substr($path, 0, 1) == "/")
		{
			/* Absolute path */
			return $path;
		}
		else
		{
			$path_elements = explode("/", $path);
			
			if(substr($path, 0, 1) == "~")
			{
				/* Home directory path */
				if(!empty($_SERVER['home']))
				{
					$homedir = $_SERVER['home'];
				}
				elseif(getenv("HOME") != null)
				{
					$homedir = getenv("HOME");
				}
				elseif(function_exists("posix_getuid") && function_exists("posix_getpwuid"))
				{
					$userinfo = posix_getpwuid(posix_getuid());
					$homedir = $userinfo['dir'];
				}
				
				$homedir = $this->RemoveTrailingSlash($homedir);
				
				$stack = explode("/", $homedir);
				array_shift($path_elements);
			}
			else
			{
				/* Relative path */
				$basepath = $this->RemoveTrailingSlash(getcwd());
				$stack = explode("/", $basepath);
			}
			
			foreach($path_elements as $element)
			{
				if($element == ".")
				{
					/* Ignore */
				}
				elseif($element == "..")
				{
					/* Go up one directory */
					if(count($stack) > 1)
					{
						array_pop($stack);
					}
					else
					{
						/* There are no elements left to pop, this is an invalid path. */
						return null;
					}
				}
				else
				{
					/* Append to path */
					$stack[] = $element;
				}
			}
			
			return implode("/", $stack);
		}
	}
}
